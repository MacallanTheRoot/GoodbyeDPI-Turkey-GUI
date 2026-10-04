import subprocess
import os
import signal
import sys
import threading
import ctypes
import atexit
import shutil
import logging
import socket
import time
from pathlib import Path
from ctypes import wintypes
from .detector import get_os, get_arch
from .paths import resource_path

logger = logging.getLogger(__name__)
STOP_TIMEOUT = 3

# Windows Job Object Constants
if os.name == 'nt':
    JOBOBJECT_EXTENDEDLIMIT_INFORMATION = 9
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [('ReadOperationCount', ctypes.c_ulonglong),
                    ('WriteOperationCount', ctypes.c_ulonglong),
                    ('OtherOperationCount', ctypes.c_ulonglong),
                    ('ReadTransferCount', ctypes.c_ulonglong),
                    ('WriteTransferCount', ctypes.c_ulonglong),
                    ('OtherTransferCount', ctypes.c_ulonglong)]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong),
                    ('PerJobUserTimeLimit', ctypes.c_longlong),
                    ('LimitFlags', ctypes.c_ulong),
                    ('MinimumWorkingSetSize', ctypes.c_size_t),
                    ('MaximumWorkingSetSize', ctypes.c_size_t),
                    ('ActiveProcessLimit', ctypes.c_ulong),
                    ('Affinity', ctypes.c_size_t),
                    ('PriorityClass', ctypes.c_ulong),
                    ('SchedulingClass', ctypes.c_ulong)]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
                    ('IoInfo', IO_COUNTERS),
                    ('ProcessMemoryLimit', ctypes.c_size_t),
                    ('JobMemoryLimit', ctypes.c_size_t),
                    ('PeakProcessMemoryUsed', ctypes.c_size_t),
                    ('PeakJobMemoryUsed', ctypes.c_size_t)]

class DNSRunner:
    def __init__(self, log_callback=None):
        self.process = None
        self.os_type = get_os()
        self.arch = get_arch(self.os_type)
        self.log_callback = log_callback
        self.output_thread = None
        self.job_handle = None
        self._lock = threading.RLock()
        
        # Last resort if the GUI never reaches its explicit shutdown path.
        atexit.register(self.stop)

    def start(self, dns_addr="77.88.8.8", dns_port="1253"):
        with self._lock:
            if self.process is not None:
                if self.process.poll() is None:
                    return
                self.stop()
            if self.os_type == 'windows':
                self._start_windows(dns_addr, dns_port)
            elif self.os_type == 'linux':
                self._start_linux(dns_addr, dns_port)
            else:
                raise NotImplementedError(f"OS {self.os_type} not supported")
            if self.log_callback and self.process.stdout is not None:
                process = self.process
                self.output_thread = threading.Thread(
                    target=self._read_output, args=(process,), daemon=True,
                    name="engine-output")
                try:
                    self.output_thread.start()
                except Exception:
                    self.stop()
                    raise

    def close(self):
        """Explicit final cleanup; retain the fallback if resources remain."""
        self.stop()
        if self.process is None and self.output_thread is None and self.job_handle is None:
            atexit.unregister(self.stop)

    def stop(self):
        with self._lock:
            process = self.process
            reaped = process is None
            if process is not None:
                try:
                    running = process.poll() is None
                except (OSError, ValueError):
                    logger.warning("Could not inspect engine; attempting to stop it", exc_info=True)
                    running = True
                if running:
                    try:
                        process.terminate()
                    except (OSError, ValueError):
                        # The process may have exited between poll and terminate.
                        logger.debug("Could not terminate engine", exc_info=True)
                reaped = self._wait_for_process(process)
                if not reaped:
                    try:
                        process.kill()
                    except (OSError, ValueError):
                        logger.debug("Could not kill engine", exc_info=True)
                    reaped = self._wait_for_process(process)

                for name in ("stdin", "stdout", "stderr"):
                    stream = getattr(process, name, None)
                    if stream is not None:
                        try:
                            stream.close()
                        except Exception:
                            # One broken stream must not prevent the other handles closing.
                            logger.warning("Could not close engine %s stream", name, exc_info=True)

            thread = self.output_thread
            reader_done = thread is None
            if thread is not None and thread is not threading.current_thread():
                try:
                    thread.join(timeout=STOP_TIMEOUT)
                    reader_done = not thread.is_alive()
                except RuntimeError:
                    # Thread.start() can fail before the reader actually starts.
                    reader_done = True

            try:
                self._close_job_handle()
            except OSError:
                logger.warning("Could not close engine Job Object", exc_info=True)

            # Closing a Windows Job Object can finish a child that resisted kill.
            if process is not None and not reaped:
                reaped = self._wait_for_process(process)
            if not reaped:
                logger.warning("Engine was not reaped during shutdown")
            if not reader_done:
                logger.warning("Engine output reader did not finish during shutdown")
            if reaped and reader_done and self.job_handle is None:
                self.process = None
                self.output_thread = None

    @staticmethod
    def _wait_for_process(process):
        try:
            process.wait(timeout=STOP_TIMEOUT)
            return True
        except subprocess.TimeoutExpired:
            return False
        except (OSError, ValueError):
            logger.warning("Could not wait for engine", exc_info=True)
            return False

    def _close_job_handle(self):
        if self.job_handle:
            ctypes.windll.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            if not ctypes.windll.kernel32.CloseHandle(self.job_handle):
                raise ctypes.WinError()
            self.job_handle = None

    def _read_output(self, process):
        """Reads stdout/stderr and sends to callback"""
        # Read line by line
        # Note: This is a simple blocking read. 
        # For merging stdout/stderr, we usually need more complex handling or just pipe stderr to stdout
        try:
             for line in iter(process.stdout.readline, b''):
                if self.log_callback:
                    self.log_callback(line.decode('utf-8', errors='replace').strip())
        except (ValueError, OSError):
            pass # Process probably closed

    def _assign_job_object(self, processes_handle):
        """Assigns the process to a Job Object that kills it on close"""
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            raise OSError("CreateJobObjectW failed")
        self.job_handle = job
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(
            job, JOBOBJECT_EXTENDEDLIMIT_INFORMATION, ctypes.pointer(info),
            ctypes.sizeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION)
        ) or not kernel32.AssignProcessToJobObject(job, processes_handle):
            self._close_job_handle()
            raise OSError("Could not assign GoodbyeDPI to a Windows Job Object")

    def _start_windows(self, dns_addr, dns_port):
        exe_path = resource_path("bin", self.arch, "goodbyedpi.exe")
        if not exe_path.is_file():
            raise FileNotFoundError(f"GoodbyeDPI executable missing: {exe_path}")
        
        args = [
            str(exe_path),
            "-5",
            "--set-ttl", "5",
            "--dns-addr", dns_addr,
            "--dns-port", dns_port,
            "--dnsv6-addr", "2a02:6b8::feed:0ff",
            "--dnsv6-port", "1253"
        ]

        # Use startupinfo to hide console window for the subprocess
        if self.os_type == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            startupinfo = None
            creation_flags = 0
            
        # Pipe output
        self.process = subprocess.Popen(
            args, 
            startupinfo=startupinfo,
            creationflags=creation_flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout
            stdin=subprocess.PIPE
        )
        
        # Assign to Job Object for clean exit
        try:
            self._assign_job_object(self.process._handle)
        except Exception:
            self.stop()
            raise

    def _start_linux(self, dns_addr, dns_port):
        executable = find_spoof_dpi()
        # SpoofDPI v0.12.0 uses plain DNS at this address and port unless
        # -enable-doh is supplied; arbitrary provider IPs need not serve DoH.
        args = [
            executable,
            "-addr", "127.0.0.1",
            "-dns-addr", dns_addr,
            "-dns-port", str(dns_port),
            "-port", "8080",
            "-system-proxy=false",
        ]
        # A listening socket is a stronger launch check than Popen succeeding.
        # Check for a pre-existing listener so it cannot be mistaken for ours.
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", 8080)) == 0:
                raise OSError("Port 8080 is already in use; close the existing proxy first.")
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                if self.log_callback and self.process.stdout is not None:
                    output = self.process.stdout.read().decode("utf-8", errors="replace").strip()
                    if output:
                        self.log_callback(output)
                self.stop()
                raise RuntimeError("SpoofDPI exited before its proxy started. Check Activity for details.")
            with socket.socket() as probe:
                probe.settimeout(0.1)
                if probe.connect_ex(("127.0.0.1", 8080)) == 0:
                    if self.process.poll() is None:
                        return
            threading.Event().wait(0.05)
        self.stop()
        raise RuntimeError("SpoofDPI did not open 127.0.0.1:8080 within 3 seconds.")


def find_spoof_dpi():
    candidates = [
        shutil.which("spoof-dpi"),
        shutil.which("spoofdpi"),
        str(Path.home() / ".spoof-dpi/bin/spoof-dpi"),
        str(Path.home() / "go/bin/spoofdpi"),
        "/usr/local/bin/spoof-dpi",
        "/usr/local/bin/spoofdpi",
        "/usr/bin/spoof-dpi",
        "/usr/bin/spoofdpi",
        "/opt/goodbyedpi-turkey/bin/spoof-dpi",
        "/opt/goodbyedpi-turkey/bin/spoofdpi",
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    logger.error("SpoofDPI executable is missing")
    raise FileNotFoundError(
        "SpoofDPI not found. Build the reviewed v0.12.0 engine with "
        "'go install github.com/xvzc/SpoofDPI/cmd/spoofdpi@v0.12.0' "
        "or install a compatible spoof-dpi/spoofdpi binary in PATH."
    )

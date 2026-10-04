import subprocess
import os
import signal
import sys
import threading
import ctypes
import atexit
import shutil
from pathlib import Path
from ctypes import wintypes
from .detector import get_os, get_arch
from .paths import resource_path

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
                    ('Affinity', ctypes.c_ulonglong),
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
    def __init__(self, base_path, log_callback=None):
        self.base_path = base_path
        self.process = None
        self.os_type = get_os()
        self.arch = get_arch()
        self.log_callback = log_callback
        self.output_thread = None
        self.job_handle = None
        self._lock = threading.RLock()
        
        # Ensure cleanup on normal exit
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
                self.output_thread.start()

    def stop(self):
        with self._lock:
            process = self.process
            if process is None:
                self._close_job_handle()
                return
            reaped = False
            try:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()  # Reap before PyInstaller removes _MEIPASS.
                reaped = True
            finally:
                thread = self.output_thread
                if thread and thread is not threading.current_thread():
                    thread.join(timeout=2)
                for name in ('stdin', 'stdout', 'stderr'):
                    pipe = getattr(process, name, None)
                    if pipe is not None:
                        try:
                            pipe.close()
                        except OSError:
                            pass
                if thread and thread.is_alive() and thread is not threading.current_thread():
                    thread.join(timeout=1)
                self._close_job_handle()
                if reaped:
                    self.process = None
                    self.output_thread = None

    def _close_job_handle(self):
        if self.job_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self.job_handle)
            finally:
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
        args = [
            executable,
            "-dns-addr", dns_addr,
            "-port", "8080", 
             "-enable-doh",
             "-window-size", "0" 
        ]
        
        self.process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
        )


def find_spoof_dpi():
    candidates = [
        shutil.which("spoof-dpi"),
        str(Path.home() / ".spoof-dpi/bin/spoof-dpi"),
        "/usr/local/bin/spoof-dpi",
        "/opt/goodbyedpi-turkey/bin/spoof-dpi",
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise FileNotFoundError(
        "SpoofDPI not found. Install a trusted spoof-dpi binary in PATH, "
        "~/.spoof-dpi/bin, /usr/local/bin, or /opt/goodbyedpi-turkey/bin."
    )

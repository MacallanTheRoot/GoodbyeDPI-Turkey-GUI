import subprocess
import os
import signal
import sys
import threading
import ctypes
import atexit
from ctypes import wintypes
from .detector import get_os, get_arch

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
        
        # Ensure cleanup on normal exit
        atexit.register(self.stop)

    def start(self, dns_addr="77.88.8.8", dns_port="1253"):
        if self.process:
            return # Already running

        if self.os_type == 'windows':
            self._start_windows(dns_addr, dns_port)
        elif self.os_type == 'linux':
            self._start_linux(dns_addr, dns_port)
        else:
            raise NotImplementedError(f"OS {self.os_type} not supported")
            
        # Start reading output
        if self.log_callback:
            self.output_thread = threading.Thread(target=self._read_output, daemon=True)
            self.output_thread.start()

    def stop(self):
        if self.process:
            # Send terminate signal
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill() # Force kill if necessary
            self.process = None
        
        # Close job handle if it exists (Windows)
        if self.job_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self.job_handle)
            except:
                pass
            self.job_handle = None

    def _read_output(self):
        """Reads stdout/stderr and sends to callback"""
        if not self.process:
            return
            
        # Read line by line
        # Note: This is a simple blocking read. 
        # For merging stdout/stderr, we usually need more complex handling or just pipe stderr to stdout
        try:
             for line in iter(self.process.stdout.readline, b''):
                if self.log_callback:
                    self.log_callback(line.decode('utf-8', errors='replace').strip())
        except (ValueError, OSError):
            pass # Process probably closed

    def _assign_job_object(self, processes_handle):
        """Assigns the process to a Job Object that kills it on close"""
        try:
            job = ctypes.windll.kernel32.CreateJobObjectW(None, None)
            self.job_handle = job

            info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

            ctypes.windll.kernel32.SetInformationJobObject(
                job,
                JOBOBJECT_EXTENDEDLIMIT_INFORMATION,
                ctypes.pointer(info),
                ctypes.sizeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION)
            )

            ctypes.windll.kernel32.AssignProcessToJobObject(job, processes_handle)
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Warning: Could not create Job Object: {e}")

    def _start_windows(self, dns_addr, dns_port):
        # Determine base path for binaries
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            # Binaries should be in internal _MEIPASS/bin
            base_dir = sys._MEIPASS
            exe_path = os.path.join(base_dir, "bin", self.arch, "goodbyedpi.exe")
        else:
            # Running from source
            # self.base_path is .../src. Binaries are in .../bin
            exe_path = os.path.join(self.base_path, "..", "bin", self.arch, "goodbyedpi.exe")
        
        exe_path = os.path.abspath(exe_path)
        
        args = [
            exe_path,
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
        if self.os_type == 'windows':
            self._assign_job_object(self.process._handle)

    def _start_linux(self, dns_addr, dns_port):
        # Look for spoof-dpi in path or local
        args = [
            "spoof-dpi",
            "-dns-addr", dns_addr,
            "-port", "8080", 
             "-enable-doh",
             "-window-size", "0" 
        ]
        
        try:
             self.process = subprocess.Popen(
                 args,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT
             )
        except FileNotFoundError:
            if self.log_callback:
                self.log_callback("Error: SpoofDPI not found. Please run install_linux.sh")
            raise FileNotFoundError("SpoofDPI not found")

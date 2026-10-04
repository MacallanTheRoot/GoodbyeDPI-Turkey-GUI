import platform

def get_os():
    return platform.system().lower()

def get_arch(os_type=None, machine=None):
    os_type = os_type or get_os()
    machine = (machine or platform.machine()).lower()
    if os_type == "windows":
        if machine in ("amd64", "x86_64"):
            return "x86_64"
        if machine in ("x86", "i386", "i686"):
            return "x86"
    elif os_type == "linux" and machine in ("amd64", "x86_64"):
        return "x86_64"
    raise NotImplementedError(f"Unsupported {os_type} architecture: {machine}")

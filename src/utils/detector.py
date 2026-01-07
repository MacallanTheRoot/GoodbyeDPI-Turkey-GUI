import platform
import os
import struct

def get_os():
    return platform.system().lower()

def get_arch():
    # Keep it simple for now, matching the batch file logic roughly
    # The batch file checks PROCESSOR_ARCHITECTURE
    machine = platform.machine().lower()
    is_64_bit = (struct.calcsize("P") * 8) == 64
    
    if is_64_bit or '64' in machine:
        return 'x86_64'
    return 'x86'

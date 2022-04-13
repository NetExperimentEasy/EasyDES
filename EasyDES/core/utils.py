import pathlib
import socket
import fcntl # windows没有
import struct

def touch_file(filename):
    """
    if path is not exited, mkdir it and touch file
    """
    filepath = pathlib.Path(filename)
    if not filepath.exists():
        filepath.parent.mkdir()
    filepath.touch(exist_ok=True)

# 此函数仅linux
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])
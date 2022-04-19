import pathlib
import socket
import struct
import platform
import msgpack

def touch_file(filename):
    """
    if path is not exited, mkdir it and touch file
    """
    filepath = pathlib.Path(filename)
    if not filepath.exists():
        filepath.parent.mkdir()
    filepath.touch(exist_ok=True)

# 此函数仅linux
sys = platform.system()
if sys != "Windows":
    import fcntl # windows没有  
    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', ifname[:15])
        )[20:24])


def encode(data):
    return msgpack.packb(data)

def decode(data):
    return msgpack.unpackb(data)
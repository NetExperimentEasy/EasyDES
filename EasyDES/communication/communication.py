import logging
from abc import abstractclassmethod, ABC
import socket
import queue
from socketserver import TCPServer, BaseRequestHandler
from threading import Thread
import time
from ..utils import encode, decode

class CommunicationBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractclassmethod
    def run_server():
        pass

    @abstractclassmethod
    def server():
        pass

    @abstractclassmethod
    def client_send():
        pass

class MyTCPHandler(BaseRequestHandler):
    # https://docs.python.org/zh-cn/3.10/library/socketserver.html
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        self.tcpqueue.put(decode(self.data))
        logging.info("{} wrote:".format(self.client_address[0]))
        logging.info(self.data)

class TCPBase(CommunicationBase):
    """
    a tcp server, \
    init: host,port \
    output: data is in the tcpqueue \
    input and output data are all encoded   \
    open a new send process once send a file or mission
    recv stop once len(recvdata)==0
    """
    def __init__(self, host=None, port=None) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.clients = {}
        self.recvsize = 1024
        self.tcpqueue = queue.Queue()

    def run_server(self):
        assert self.host is not None , "server must set host"
        assert self.port is not None , "server must set port"
        self.server()

    def server(self):
        addr = (self.host, self.port)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(addr)
        logging.info("server is created successful")
        sock.listen()
        logging.info("server is listening")
        while True:
            # Establish connection with client.
            client, addr = sock.accept()    
            logging.info(f'Got connection from {addr}')
            t = Thread(target=self._deal_data, args=(client, addr))
            self.clients[addr] = client
            t.start()

    def _deal_data(self, c, addr):
        alldata = b''
        while True:
            data = c.recv(self.recvsize)
            if len(data) == 0:
                # if file recv finished??? break and save it in the queue
                # c.close()
                # del self.clients[addr]
                break
            else:
                alldata += data
        self.tcpqueue.put(decode(alldata))
        logging.info(f'Got data {alldata}')
        
    
    def client_send(self, aim_ip, aim_host, data):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((aim_ip, aim_host))
        self.send(data=data, sock=sock)
        sock.close()

    def send(self, data, sock=None,addr=None):
        if addr:    # ???????????????????????????
            if addr in self.clients.keys():
                client = self.clients[addr]
                client.sendall(encode(data))
                logging.info(f'send data to {addr}')
        elif sock:   # ???????????????????????????
            sock.sendall(encode(data))
            logging.info(f'send {data} to {sock}')
        else:
            logging.info('nothing happended')
            return



class UDPBase(CommunicationBase):
    """
    a udp server  \
        (decode and encode)   \
    recv udp data , save it to udpquque  \
    send udp data  \
    init: host,port \
    output: data is in the udpqueue \
        input and output data are all encoded and decoded
    """
    def __init__(self, host=None, port=None) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.udpqueue = queue.Queue()

    def run_server(self):
        assert self.host is not None , "server must set host"
        assert self.port is not None , "server must set port"
        self.server()

    def server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        logging.info("udp server started")
        while True:
            data, addr = sock.recvfrom(1024)
            # logging.debug(f"udp server rev {decode(data)} from {addr}")
            self.udpqueue.put((decode(data),addr))

    def client_send(self, aim_ip, aim_port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if aim_ip == '<broadcast>':
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
        sock.sendto(encode(data), (aim_ip, aim_port))
        # logging.info(f"udp send to {aim_ip} succeed")

    def send(self, aim_ip, aim_port, data):
        self.client_send(aim_ip, aim_port, data)

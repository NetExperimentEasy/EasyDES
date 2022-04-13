import logging
from abc import abstractclassmethod, ABC
import socket
import queue
from socketserver import TCPServer, BaseRequestHandler
import traceback
from threading import Thread

class CommunicationBase(ABC):
    def __init__(self) -> None:
        pass

class MyTCPHandler(BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)
        self.queue = queue

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)

class Communication(CommunicationBase):
    """
    worker run a tcp server
    """
    def __init__(self) -> None:
        super().__init__()
        self.queue = queue.Queue()

    def run_communication(self, host, port):
        t1 = Thread(target=self.tcp_server, args=(host, port))
        t2 = Thread(target=self.deal_data)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def tcp_server(self, host, port):
        addr = (host, port)
        with TCPServer(addr, MyTCPHandler(self.queue)) as server:
            server.serve_forever()

    def tcp_send(self, ip, port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, port))


# 节点通信  communication

# 
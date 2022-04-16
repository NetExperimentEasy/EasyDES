import logging
from abc import abstractclassmethod, ABC
import socket
import queue
from socketserver import TCPServer, BaseRequestHandler
from threading import Thread
import time

class CommunicationBase(ABC):
    def __init__(self) -> None:
        pass

class MyTCPHandler(BaseRequestHandler):

    def __init__(self, request, client_address, server, tcpqueue:queue.Queue) -> None:
        super().__init__(request, client_address, server)
        self.tcpqueue = tcpqueue

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        self.tcpqueue.put(self.data)
        logging.info("{} wrote:".format(self.client_address[0]))
        logging.info(self.data)

class TransportServer(CommunicationBase):
    """
    a tcp server, \
    init: host,port \
    output: data is in the tcpqueue
    """
    def __init__(self, host, port) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.tcpqueue = queue.Queue()

    def run_server(self):
        self.tcp_server(self.host, self.port)

    def tcp_server(self, host, port):
        addr = (host, port)
        with TCPServer(addr, MyTCPHandler(self.tcpqueue)) as server:
            server.serve_forever()

    def tcp_send(self, aim_ip, aim_port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (aim_ip, aim_port))



class ControllerServer(CommunicationBase):
    """
    ControllerServer : a udp server  \
    recv udp data , save it to udpquque  \
    send udp data  \
    init: host,port \
    output: data is in the udpqueue
    """
    def __init__(self, host, port) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.udpqueue = queue.Queue()

    def run_server(self):
        self.tcp_server(self.host, self.port)

        if self.type == "worker":
            t1 = Thread(target=self.worker_udp_client)
            t2 = Thread(target=self.worker_udp_server)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif self.type == "controller":
            t1 = Thread(target=self.controller_udp_server)
            t2 = Thread(target=self.controller_udp_client) 
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        else:
            raise ValueError("CommunicationHub.type error")
    
    def udp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        logging.info("udp server started")
        while True:
            data, addr = sock.recvfrom(1024)
            logging.debug(f"udp server rev {data.decode()} from {addr}")
            self.udpqueue.put(data.decode())
    # 220416 stop 
    
    def controller_udp_server(self):
        """
        程序运行中，持续运行
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))
        logging.info(f"controller udp server started bind on {self.port}")
        while self.flag:
            data, addr = sock.recvfrom(1024)
            logging.info(f"controller udp server rev {data.decode()} from {addr}")
            if data.decode() == addr and addr != '':
                """
                controller udp server
                recv: 1. 广播出去的包， 2. worker发送来的注册信息(worker端的ip)
                addr,数据包的源ip，if addr == self.ip -> 广播包 : 跳过
                data.decode(),worker数据包内的信息， if data.decode() 不在已有的ip池 则注册该ip
                """
                if addr != self.ip:
                    ip = data.decode()
                    if ip not in self.node_pool:
                        self.register(ip)
                        self.controller_reply_worker(ip)
        sock.close()
        return False

    def controller_reply_worker(self, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info(f"controller reply worker {ip}")
        sock.sendto(f'{ip}'.encode(), (ip, self.port))
        logging.info(f"reply succeed")
        return True
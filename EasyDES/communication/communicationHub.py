from .communication import TCPBase, UDPBase
from threading import Thread
import logging
import time

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class BaseTransport(TCPBase):
    """
    replay ack 
    """

    def ack(self, aim_ip, aim_port, data):
        self.send(aim_ip, aim_port, data)

# TODO : change this

class BaseControllerServer(UDPBase):
    """
    register Hub
    detect clients， reply msg
    special controller instructions
    """
    def __init__(self, host, port) -> None:
        super().__init__(host, port)
        self.node_pool = []

    def run(self):
        t1 = Thread(target=self.run_server)
        t2 = Thread(target=self.deal_udpqueue)
        t1.start()
        t2.start()
        t1.join()
        t2.join()


    def deal_udpqueue(self):
        """
        deal with all udpqueue : [data had been decoded]
        """
        while True:
            data, addr = self.udpqueue.get(True)
            logging.info(f"deal with data: {data} from {addr}")
            if type(data) == tuple:
                self.discover(data, addr)

    def register(self, ip, port):
        self.node_pool.append((ip, port))  

    def discover(self, data, addr):
        if data[0] == addr and addr != '':
            """
            recv: 1. 广播出去的包， 2. worker发送来的注册信息(worker端的ip)
            addr,数据包的源ip，if addr == self.ip -> 广播包 : 跳过
            data,worker数据包内的信息， if data 不在已有的ip池 则注册该ip
            """
            if addr != self.host:
                ip, port = data
                if ip not in self.node_pool:
                    self.register((ip, port))
                    self.controller_reply_worker(ip)

    # instructions
    def controller_reply_worker(self, aim_ip, aim_port):
        """
        controller reply worker: (worker's ip, controller's ip, controller's port)
        """
        self.send(aim_ip, aim_port, (aim_ip, self.host, self.port))
        logging.info(f"reply to {aim_ip} succeed")

    def sendall_start(self):
        """
        instruction: start all missions: "start": [string]
        """
        for ip, port in self.node_pool:
            self.send(ip, port, "start")
            logging.info(f" {ip} succeed")

class BaseControllerClient(UDPBase):
    """
    recv instructions:
    1. reply from controller
    2. start instruction
    3. etc
    send:
    1. self register information: (self.host,self.port)
    2. ack : started 
    """
    _IF_SEND=True
    controller_ip = None
    controller_port = None

    def run_server(self):
        t0 = Thread(target=self.send_register)
        t1 = Thread(target=self.server)
        t2 = Thread(target=self.deal_queue)
        t0.start()
        t1.start()
        t2.start()
        t0.join()
        t1.join()
        t2.join()

    def deal_queue(self):
        """
        deal with all data
        """
        while True:
            data, addr = self.udpqueue.get(True)
            logging.debug(f"deal with data: {data} from {addr}")
            if type(data) == tuple:
                self.reply_from_controller(data)
            self.instruction_start(data)

    def send_register(self):
        IP_255 = self.host[:self.host.rindex('.')]+'.255'
        if self._IF_SEND:
            # needs to be fixed: can't got aim port before register, how to boardcast?
            # now： only can keep each side node's port same
            self.send(IP_255, self.port, (self.host, self.port))
            time.sleep(2)

    def send_ack_start(self):
        self.send(self.controller_ip, self.controller_port, "started")
    
    # instructions
    def reply_from_controller(self, data):
        """
        reply from contriller: if data[0] is the worker's ip: [string], register succeed
        """
        if data[0] == self.host:
            self._IF_SEND = False
            self.controller_ip = data[1]
            self.controller_port = data[2]
            logging.info(f"registe succeed and stop the register sender")

    def instruction_start(self, data, func):
        """
        instruction: start all missions: "start": [string]
        func: callable function for mission to start all missions or add instruction to a instructions list(different from the missions list)
        """
        if data == "start":
            func()
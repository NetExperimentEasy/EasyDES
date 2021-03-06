import queue
from .communication import TCPBase, UDPBase
from threading import Thread
import logging
from copy import deepcopy
from .instruction import registerInstruction, registeredReplyInstruction, missionStartInstruction, startedReplyInstruction
from ..missions.instruction import runAllMissions
import time

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class BaseTransport(TCPBase):
    """
    replay ack 
    """

    def ack(self, aim_ip, aim_port, data):
        # create a new tcp to ack
        self.send(aim_ip, aim_port, data)


class BaseController(UDPBase):
    """
    register Hub
    detect clients， reply msg
    special controller instructions
    """
    def __init__(self, host=None, port=None) -> None:
        super().__init__(host, port)
        self.node_pool = []

    def runController(self):
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
            if data["type"] == "registerInstruction":
                self.discover(data, addr)
            elif data["type"] == "startedReplyInstruction":
                self.started_reply(data, addr)
            
    def node_register(self, ip, port):
        self.node_pool.append((ip, port))  

    def discover(self, data, addr):
        ip, port = addr
        if data["w_ip"] == ip and ip != '':
            """
            recv: 1. 广播出去的包， 2. worker发送来的注册信息(worker端的ip)
            addr,数据包的源ip，if addr == self.ip -> 广播包 : 跳过
            data,worker数据包内的信息， if data 不在已有的ip池 则注册该ip
            """
            if ip != self.host:
                w_ip, w_port = data["w_ip"], data["w_port"]
                if w_ip not in self.node_pool:
                    self.node_register(w_ip, w_port)
                    self.registered_reply(w_ip, w_port)

    def registered_reply(self, w_ip, w_port):
        """
        controller reply worker: (worker's ip, controller's ip, controller's port)
        """
        data = deepcopy(registeredReplyInstruction)
        data["w_ip"] = w_ip
        data["c_ip"] = self.host
        data['c_port'] = self.port
        self.send(w_ip, w_port, data)
        logging.info(f"reply to {w_ip} succeed")

    # 由于manager是任务队列，所以目前只能实现start all命令
    def sendall_start(self, uuid="all"):
        """
        instruction: start all missions: uuid==all, spectial: uuid==uuid
        """
        data = deepcopy(missionStartInstruction)
        data["uuid"] = uuid
        for ip, port in self.node_pool:
            self.send(ip, port, data)
            logging.info(f"send instruction:[start:{uuid}] to {ip} : succeed")
    
    # 由于manager是任务队列，所以目前只能实现start all命令
    def send_start(self, aim_ip, aim_port, uuid="all"):
        data = deepcopy(missionStartInstruction)
        data["uuid"] = uuid
        self.send(aim_ip, aim_port, data)
        logging.info(f"send instruction:[start:{uuid}] to {aim_ip} : succeed")

    def started_reply(self, data, addr):
        uuid = data["uuid"]
        logging.info(f"{addr} : mission : {uuid} started!")

class BaseWorker(UDPBase):
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

    def runWorker(self):
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
            if data["type"] == "registeredReplyInstruction":
                self.deal_registered_reply(data, addr)
            elif data["type"] == "missionStartInstruction":
                assert self.runqueue ,ValueError("mission_start instruction needs set runqueue first")
                self.mission_start(data, self.runqueue)

    def send_register(self):
        # IP_255 = self.host[:self.host.rindex('.')]+'.255'
        IP = '<broadcast>' 
        data = deepcopy(registerInstruction)
        data["w_ip"] = self.host
        data["w_port"] = self.port
        while self._IF_SEND:
            # needs to be fixed: can't got aim port before register, how to boardcast?
            # now： only can keep each side node's port same
            self.send(IP, self.port, data)
            time.sleep(2)

    def mission_started_reply(self, uuid):
        data = deepcopy(startedReplyInstruction)
        data["uuid"] = uuid
        self.send(self.controller_ip, self.controller_port, data)
        logging.info(f"mission {uuid} started reply to {self.controller_ip}:{self.controller_port} succeed")
    
    def deal_registered_reply(self, data, addr):
        """
        reply from controller: if data["w_ip"] is the worker's ip: [string], register succeed
        notice: server will set its ip 0.0.0.0, but worker should use its ip from addr rather than it in data
        notice2: server's port should use data's c_port, beacause addr port are random value
        """
        if data["w_ip"] == self.host:
            self._IF_SEND = False
            self.controller_ip, _  = addr
            self.controller_port = data["c_port"]             
            logging.info(f"register succeed and stop the register sender")

    def mission_start(self, data, runqueue: queue.Queue):
        """
        instruction: start all missions: "start": [string]
        put a start instruction to global runtime queue, missionHub received and start missions
        func: callable function for mission to start all missions or add instruction to a instructions list(different from the missions list)
        """
        # 当前版本 只有startall的功能，如需扩展，需修改mission_manager中的任务队列为其他数据结构
        uuid = data["uuid"]
        if data["uuid"] == "all":
            logging.info(f"recev mission {uuid} : start")
            data = deepcopy(runAllMissions)
            runqueue.put(runAllMissions)
            self.mission_started_reply(uuid)
        # data = deepcopy(runMission)
        # data["uuid"] = uuid
        # runqueue.put(runMission)
        # start uuid one          

    def set_common_queue(self, runqueue: queue.Queue):
        self.runqueue = runqueue
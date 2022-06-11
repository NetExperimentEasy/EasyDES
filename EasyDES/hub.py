
# Todo : delete



import logging
import uuid
import socket
from abc import abstractclassmethod, ABC
from dataclasses import dataclass
from .missions.mission import MissionManager, Mission
from .communication.communication import Communication
from .utils import get_ip_address
import time
from threading import Thread
import msgpack
from .utils import touch_file

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class HubBase(ABC):
    """
    Hub:注册中心 :单例  :Singleton
    MissionsHub
    CommunicationHub
    """
    def __new__(cls, type):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(CommunicationHub, cls).__new__(cls)
        return cls.instance

@dataclass
class CommunicationHubItem:
    ip:str
    introduction:str=None

class CommunicationHub(HubBase, Communication):
    """
    网络控制中心,每个Node上跑一个单例，负责维护和其他节点的通信
    发现节点\   udp广播发现，worker端进行udp广播，Controller端进行udp发现
        具体过程:
            worker端:运行一个_udp_client，广播自己的ip；_udp_server,接受回复，收到广播后，判断是否自己ip，是则关闭_udp_client和_udp_server
            controller端:长时间运行一个服务server,接受ip，并存入node_pool，同时向对应worker回复应答。
            广播包，自己会收到自己的包，所以要过滤掉这种信息
    以下功能由Communication类提供
    心跳维护\暂时不要
    失效节点清除\暂时不要
    具体的传输功能，序列化，反序列化
    """
    def __init__(self, type, eth, port=5254) -> None:
        """
        type : [worker]/[controller]
        eth : interface name
        """
        super().__init__()
        self.type = type
        self.ip = ''
        self.eth = eth
        if eth:
            self.ip=get_ip_address(eth)
            assert self.ip , "interface has no ip"
        self.port = port
        self.flag = True    # flag: control if udp lient run
        self.experiment = False     # Mission系统靠这个关键字开启试验
        if self.type == "worker":
            self.node_pool = None
        elif self.type == "controller":
            self.node_pool = [] # ip list
        else:
            raise ValueError("CommunicationHub.type error")    
        # self.communication = Communication()
    
    def run_udp(self):
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

    def register(self, ip):
        self.node_pool.append(CommunicationHubItem(ip))   

    def worker_udp_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info("worker udp client started")
        while self.flag:
            #获取本机IP
            if self.ip=='' or not self.ip:
                IP = socket.gethostbyname(socket.gethostname())
            else:
                IP = self.ip
            #255表示广播地址
            IP_255 = IP[:IP.rindex('.')]+'.255'
            #发送信息
            sock.sendto(f'{IP}'.encode(), (IP_255, self.port))
            logging.info(f"worker udp client send {IP} to {IP_255}")
            time.sleep(1)
        logging.info(f"worker has registered, quit")
        return
    
    def worker_udp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info("worker udp server started")
        sock.bind((self.ip, self.port))
        while True:
            data, addr = sock.recvfrom(1024)
            logging.info(f"worker udp server rev {data.decode()} from {addr}")
            if addr != self.ip and data.decode() == addr: 
                """
                work udp server
                recv: 1. 广播出去的包， 2. controller返回来的确认信息(接收端的ip)
                addr,数据包的源ip，if addr == self.ip -> 广播包 : 跳过
                data.decode(),服务端返回的数据包内的信息， if data.decode() == self.ip -> 服务端的包 :  注册成功
                """
                logging.info(f"worker udp server data.decode() == addr ? {data.decode() == addr} ")
                self.flag = False   # 结束worker的client
                # sock.close()
                # return True
            if data.decode() == "start":
                # start,开始任务运行
                self.experiment = True
    
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

class MissionHubBase(HubBase):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractclassmethod
    def register(self):
        # 注册任务
        pass

    @abstractclassmethod
    def send():
        pass

@dataclass
class MissionHubItem:
    UUID:str
    creator:str
    introduction:str
    mission:Mission


# old class need delete
class MissionHub(MissionHubBase, MissionManager):
    """
    任务注册中心,每个Node上跑一个，通过网络注册单例进行通信
    对于Controller节点，管理者手动创建新的任务类型，调用对应方法进行注册 UUID。
    注册之后，调用对应的方法分发任务。
        如果目标节点的MissionHub没有该任务，则通信模块发送代码，并在目标节点注册任务。
    分发任务，Hub只负责发布(任务UUID,添加次数)，各个节点的MissionManager据此负责任务挂载
    """
    def __init__(self, type, eth) -> None:
        super().__init__()
        # self.log_file = "missonHub.log"
        self.missions_pool = []
        self.uuid_list = [] # save uuid, 判断任务是否存在
        self.communication = CommunicationHub()
    
    def run():
        """
        run MissionHub
        """
        pass
    
    def register(self, mission:Mission=None, mission_item:MissionHubItem=None, creator=None, introduction=None, if_new=False):
        # 注册任务, if_new : Ture, register a new mission to Hub, False, register a exist mission to Hub
        if if_new:
            assert mission , "register new mission, can not be None"
            new_uuid = uuid.uuid4()
            self.missions_pool.append(MissionHubItem(new_uuid, creator, introduction, mission))
            self.uuid_list.append(new_uuid)
        else:
            self.missions_pool.append(mission_item)
            self.uuid_list.append(mission_item.UUID)

    def if_mission_exist(self, uuid):
        return uuid in self.uuid_list

    def send_mission(self, ip, port, missionHubItem:MissionHubItem):
        data = msgpack.packb({"missionHubItem":missionHubItem})
        self.communication.tcp_send(ip, port, data)
        if missionHubItem.mission.mission_type == "file_path":
            with open(f'./missions/{missionHubItem.mission}', "r") as f:
                file = msgpack.packb({"file":f.read(),"filename":missionHubItem.mission.mission})
                self.communication.tcp_send(ip, port, file)

    def receive_mission(self):
        while True:
            data = self.communication.queue.get(True)
            obj = msgpack.unpackb(data)
            if 'missionHubItem' in obj:
                missionHubItem = obj['missionHubItem']
                self.register(if_new=False,mission_item=missionHubItem)
            if 'file' in obj:
                file = obj['file']
                filename = obj['filename']
                touch_file(filename=filename)
                with open(filename,'w') as f:
                    f.write(file)

        
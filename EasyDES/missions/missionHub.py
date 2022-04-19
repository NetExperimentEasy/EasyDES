from abc import abstractclassmethod
from dataclasses import dataclass
from .mission import Mission, MissionManager
import uuid
import logging
from ..utils import touch_file

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class MissionHubBase:
    def __init__(self) -> None:
        pass
    
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

class MissionHub(MissionHubBase, MissionManager):
    """
    任务注册中心,每个Node上跑一个，通过网络注册单例进行通信
    对于Controller节点，管理者手动创建新的任务类型，调用对应方法进行注册 UUID。
    注册之后，调用对应的方法分发任务。
        如果目标节点的MissionHub没有该任务，则通信模块发送代码，并在目标节点注册任务。
    分发任务，Hub只负责发布(任务UUID,添加次数)，各个节点的MissionManager据此负责任务挂载
    """
    def __init__(self) -> None:
        super().__init__()
        # self.log_file = "missonHub.log"
        self.missions_pool = []
        self.uuid_list = [] # save uuid, 判断任务是否存在
    
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

    def mission_to_data(self, missionHubItem:MissionHubItem):
        data = [{"missionHubItem": missionHubItem}]
        if missionHubItem.mission.mission_type == "file_path":
            with open(f'./missions/{missionHubItem.mission}', "r") as f:
                file = {"file":f.read(),"filename": missionHubItem.mission.mission}
                data.append(file)
        return data

    def data_received_to_mission(self, data):
        for obj in data:
            if 'missionHubItem' in obj:
                missionHubItem = obj['missionHubItem']
                self.register(if_new=False,mission_item=missionHubItem)
            if 'file' in obj:
                file = obj['file']
                filename = obj['filename']
                touch_file(filename=filename)
                with open(filename,'w') as f:
                    f.write(file)

        
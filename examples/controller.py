from EasyDES.communication.communicationHub import BaseController
from EasyDES.missions.missionHub import MissionHub
from time import sleep
from multiprocessing import Process
from threading import Thread
from EasyDES.missions.mission import Mission
import logging
import queue

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class Controller(BaseController, MissionHub):
    def __init__(self, **kwargs) -> None:
        super().__init__(*kwargs)
        self.host="0.0.0.0"
        self.port=5686
        runmission_queue = queue.Queue()
        self.set_common_queue(runqueue=runmission_queue)

    def run(self):
        # 这里多线程，因为跨线程需要通信管道
        p1 = Thread(target = super().runController)
        p2 = Thread(target= super().runMissionHub)
        p1.start()
        p2.start()
        sleep(10)
        code = "print(2+3)"
        a = Mission(mission_type="string",mission=code , python=True)
        self.mission_register(mission=a, if_new=True)
        logging.info(self.missions_pool)
        b = self.missions_pool[0] # MissionHubItem
        self.mission_register(mission_item=b)
        logging.info(self.missions_pool)
        self.sendall_start()
        self.put_mission(a)
        self.put_mission(b.mission) 
        self.put_mission(a)
        # self.run_all_missions() #运行报错
        p1.join()


a = Controller()
a.run()
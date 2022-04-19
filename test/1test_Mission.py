import pytest
import logging
from EasyDES.missions.mission import MissionManager, Mission

logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class TestMission:
    def test_python(self):
        # python 字符串型命令 执行
        code = """
        this
        """
        a = Mission(mission_type="string",mission=code , python=True)
        logging.info(a.get_command())

class TestMissionManager:
    def test_python(self):
        code = "this"
        a = Mission(mission_type="string",mission=code , python=True)
        b = MissionManager()
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a)
        while not self.missions_queue.empty():
            priority, mission = self.get_mission()
            print(priority, mission)
        # b.run_all_missions(log_file='log.log')

A = TestMissionManager()
A.test_python()
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
        code = "print(2+3)"
        code2 = "print(1+2)"
        a = Mission(mission_type="string",mission=code , python=True)
        a2 = Mission(mission_type="string",mission=code2 , python=True)
        b = MissionManager()
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a2)
        # while not b.missions_queue.empty():
        #     priority, mission = b.get_mission()
        #     print(priority, mission)
        b.run_all_missions(log_file='log.log')

    def test_python_file(self):
        file1 = "python1.py"
        file2 = "python2.py"
        a = Mission(mission_type="file_path",mission=file1 , python=True)
        a2 = Mission(mission_type="file_path",mission=file2 , python=True)
        b = MissionManager()
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a2)
        b.run_all_missions(log_file='log.log')

    def test_bash_file(self):
        file1 = "bash1.sh"
        file2 = "bash2.sh"
        a = Mission(mission_type="file_path",mission=file1 , bash=True)
        a2 = Mission(mission_type="file_path",mission=file2 , bash=True)
        b = MissionManager()
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a2)
        b.run_all_missions(log_file='log.log')

    def test_bash(self):
        bash1 = "ping www.seclee.com -c 5 > logs/ping1.log"
        bash2 = "ping www.baidu.com -c 20 > logs/ping2.log"
        a = Mission(mission_type="string",mission=bash1 , bash=True)
        a2 = Mission(mission_type="string",mission=bash2 , bash=True)
        b = MissionManager()
        b.put_mission(a)
        b.put_mission(a)
        b.put_mission(a2)
        b.run_all_missions(log_file='log.log')

A = TestMissionManager()
A.test_bash()
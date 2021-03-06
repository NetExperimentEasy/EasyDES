import queue
import logging
import datetime
import time
from subprocess import Popen, PIPE
from abc import abstractclassmethod, ABC
from ..utils import touch_file
from collections import namedtuple
from multiprocessing import Process

class MissionBase(ABC):
    # MISSION_TYPE = [
    #     "bash",  # cmd line
    #     "python"  # python script
    # ]
    pass
    
class MissionManagerBase(ABC):
    @abstractclassmethod
    def put_mission(self, mission):
        pass
    
    @abstractclassmethod
    def pop_mission(self):
        pass

    @abstractclassmethod
    def run_mission(self):
        "run cmd"
        pass

    def __len__(self) -> int:
        return self.missions_queue.qsize()


class BashMissionMixin:
    def __init__(self) -> None:
        self.bash = False

    def run_bash(self):
        pass

class PythonMissionMixin:
    def __init__(self) -> None:
        self.python = False

    def run_python(self):
        pass

class Mission(MissionBase, BashMissionMixin, PythonMissionMixin):
    """
    Mission class \\
    [parameters]:
        mission : reuqired : Default is None : Expected type are [string]/[file_path]
        python : optional : Default is False : If True, mission type is python script
        bash : optional : Default is False : If True, mission type is bash script
        priority : optional : Default is 5 : 1 is the highest priority
    """
    def __init__(self, mission_type, mission, python=False, bash=False, priority=5) -> None:
        super().__init__()
        self.mission_type = mission_type
        self.mission = mission
        self.priority = priority
        self.created_time = time.mktime(datetime.datetime.now().timetuple())
        self.python = python
        self.bash = bash
        assert self.python^self.bash , SyntaxError("python and bash can not be True/False at same time")

    def get_command(self):
        if self.python:
            return self._get_python_cmd()
        elif self.bash:
            return self._get_bash_cmd()
        else:
            raise SyntaxError("Mission Type Error")

    def _get_python_cmd(self):
        if self.mission_type == "string":
            return f'python -c \"{self.mission}\"'  # ?????? -c ???????????????
        if self.mission_type == "file_path":
            return f"python ./missions/{self.mission}"  # ????????????????????????mission???????????????
        raise SyntaxError("mission_type Type Error")
    
    def _get_bash_cmd(self):
        if self.mission_type == "string":   # ?????????python???????????????????????????bash???string??????
            return self.mission
        if self.mission_type == "file_path":
            return f"bash ./missions/{self.mission}"  # ????????????????????????mission???????????????
        raise SyntaxError("mission_type Type Error")

    def __lt__(self, other_mission):
        return self.created_time > other_mission.created_time


mission_item = namedtuple('mission_item', ['priority', 'mission'])

class MissionManager(MissionManagerBase):
    """
    MissionManager: ????????????????????????Hub?????????
    ??????????????????????????????
    ?????????????????????????????????
    ???????????????
    """
    missions_queue = queue.PriorityQueue()
    def __init__(self) -> None:
        super().__init__()
        
    def put_mission(self, mission:Mission):
        self.missions_queue.put(mission_item(mission.priority, mission))

    def pop_mission(self) -> Mission:
        return self.missions_queue.get()

    def run_all_missions(self, log_file=None):
        result = []
        while not self.missions_queue.empty():
            priority, mission = self.pop_mission()
            p = Process(target=self.run_mission, args=(mission.get_command(), log_file))
            p.start()
            result.append(p)
        for i in result:
            i.join()
        return result
        # TODO: window????????????linux?????????

    def run_mission(self, cmd, log_file=None):
        """
        run mission, set log_file if write log to file
        """
        def run_cmd(cmd):
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            logging.info("{}".format(stdout))
            if stderr:
                logging.error("Got error when running cmd: {}".format(cmd))
                return stdout, stderr
            return stdout, "Successed"

        if log_file:
            touch_file(f"./logs/{log_file}")
            with open(f"./logs/{log_file}", 'a') as f:
                f.write(f"{datetime.datetime.now()}:{cmd} \n")
                stdout, stderr = run_cmd(cmd)
                # f.write(f"[result]:{stderr},[output]:{stdout}:\n")
                f.write(f"[result]:{stderr}\n")
        else:
            stdout, stderr = run_cmd(cmd)
        return stdout
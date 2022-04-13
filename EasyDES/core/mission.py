import queue
import logging
import datetime
import os
from subprocess import Popen, PIPE
from abc import abstractclassmethod, ABC
from .utils import touch_file

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
    def get_mission(self):
        pass

    @abstractclassmethod
    def run():
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
    """
    def __init__(self, mission_type, mission, python=False, bash=False) -> None:
        super().__init__()
        self.mission_type = mission_type
        self.mission = mission
        if python:
            self.python = True
        elif bash:
            self.bash = True
        else:
            raise SyntaxError("You can not init a mission without Type")

    def get_command(self):
        if self.python:
            return self._get_python_cmd()
        elif self.bash:
            return self._get_bash_cmd()
        else:
            raise SyntaxError("Mission Type Error")

    def _get_python_cmd(self):
        if self.mission_type == "string":
            return f"python -m {self.mission}"  # 单指 -m 后面的命令
        if self.mission_type == "file_path":
            return f"python ./missions/{self.mission}"  # 这块先写死了下发mission文件的目录
        raise SyntaxError("mission_type Type Error")
    
    def _get_bash_cmd(self):
        if self.mission_type == "string":   # 如果是python执行文件，传参，用bash的string命令
            return self.mission
        if self.mission_type == "file_path":
            return f"bash ./missions/{self.mission}"  # 这块先写死了下发mission文件的目录
        raise SyntaxError("mission_type Type Error")


class MissionManager(MissionManagerBase):
    """
    MissionManager: 任务管理器，混入Hub中使用
    负责任务的调度，执行
    当前实现，先进先出队列
    TODO.优先级队列
    """
    def __init__(self) -> None:
        super().__init__()
        self.missions_queue = queue.Queue()
        
    def put_mission(self, mission:Mission):
        self.missions_queue.put(mission)
    
    def put_mission(self, mission:Mission):
        self.missions_queue.put(mission)

    def get_mission(self) -> Mission:
        return self.missions_queue.get()

    def run_mission(self, log_file=None):
        mission_item = self.get_mission()
        return self.run(mission_item.get_command(), log_file)

    def run(self, cmd, log_file=None):
        """
        run mission, set log_file if write log to file
        """
        def run_cmd(cmd):
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if stderr:
                logging.error("Got error when running cmd: {}".format(cmd))
                return stdout, stderr
            return stdout, "Successed"

        if log_file:
            touch_file(f"./logs/{log_file}")
            with open(f"./logs/{log_file}", 'w') as f:
                f.write(f"{datetime.datetime.now()}:{cmd} \n")
                stdout, stderr = run_cmd(cmd)
                f.write(f"{stdout}:{stderr}")
        else:
            stdout, stderr = run_cmd(cmd)
        return stdout
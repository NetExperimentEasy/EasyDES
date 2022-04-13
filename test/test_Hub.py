import pytest
from EasyDES.core.hub import MissionHub
from EasyDES.core.mission import Mission
import queue

class TestMissionHubBase:
    a = MissionHub()
    b = MissionHub()

    def test_Singleton(self): 
        assert isinstance(self.a, MissionHub)
        assert isinstance(self.b, MissionHub)
        assert self.a is self.b , "MissionHub is not a Singleton Class"
    
    def test_SharedQueue(self):
        assert isinstance(self.a.missions_queue, queue.Queue)
        code = "this"
        item = Mission(mission_type="string",mission=code , python=True)
        self.a.put_mission(item)
        b_item = self.b.get_mission()
        assert b_item is item , "not shared Queue"

        


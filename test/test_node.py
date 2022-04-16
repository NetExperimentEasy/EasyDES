import pytest
from EasyDES.node import Worker, Controller, WorkerType


class TestMissionHubBase:
    def test_WorkerNode(self):
        for item in WorkerType:
            a = Worker("testname", item.value)
            assert a.type is item, 'type error'

        


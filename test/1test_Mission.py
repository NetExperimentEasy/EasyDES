# import pytest
# import logging
# from EasyDES.missions.mission import MissionManager, Mission

# class TestMission:
#     def test_python(self):
#         # python 字符串型命令 执行
#         code = """
#         this
#         """
#         a = Mission(mission_type="string",mission=code , python=True)
#         print(a.get_command())

# class TestMissionManager:
#     def test_python(self):
#         code = "this"
#         a = Mission(mission_type="string",mission=code , python=True)
#         b = MissionManager()
#         b.put_mission(a)
#         b.run_mission(log_file='log.log')

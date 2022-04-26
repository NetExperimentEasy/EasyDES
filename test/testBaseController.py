from EasyDES.communication.communicationHub import BaseController
from time import sleep

a = BaseController('0.0.0.0', 5686)

a.run()
sleep(5)
a.sendall_start()
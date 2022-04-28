from EasyDES.communication.communicationHub import BaseController
from time import sleep
from threading import Thread

a = BaseController('0.0.0.0', 5686)

t1 = Thread(target=a.run)

t1.start()
t1.join()
sleep(10)
a.sendall_start()
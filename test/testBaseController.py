from EasyDES.communication.communicationHub import BaseController
from time import sleep
from threading import Thread

a = BaseController('0.0.0.0', 5686)

t1 = Thread(target=a.run)
t2 = Thread(target=a.sendall_start)

t1.start()
sleep(10)
t2.start()

t1.join()
t2.join()
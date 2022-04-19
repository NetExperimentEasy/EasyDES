from EasyDES.communication import UDPBase
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


c = UDPBase()
# data = {'test':11111}

data2 = 'find'

# with open('tran.txt','r') as f:
    # data2 = f.read()

c.client_send(aim_ip='0.0.0.0',aim_port=5686, data= data2)



from EasyDES.communication.communication import TCPBase
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


c = TCPBase('0.0.0.0', 55568)
# data = {'test':11111}

data2 = 'find'

# with open('tran.txt','r') as f:
    # data2 = f.read()

c.client_send('0.0.0.0',5686, data2)



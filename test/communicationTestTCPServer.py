from EasyDES.communication import TCPBase
import logging
from threading import Thread

logging.basicConfig(level=logging.DEBUG,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


s = TCPBase()

def deal_data(queue):
    while True:
        data = queue.get(True)
        logging.info(f'got data from queue {data}')

t1 = Thread(target = s.run_server)
t2 = Thread(target = deal_data, args=(s.tcpqueue,))
t1.start()
t2.start()
t1.join()
t2.join()



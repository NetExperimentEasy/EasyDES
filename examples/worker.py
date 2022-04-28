from EasyDES.communication.communicationHub import BaseWorker
import queue

a = BaseWorker('172.17.0.3', 5686)
runmission_queue = queue.Queue()
a.set_common_queue(runqueue=runmission_queue)

a.run()
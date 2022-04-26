from EasyDES.communication.communicationHub import BaseWorker

a = BaseWorker('172.17.0.2', 5686)

a.run()
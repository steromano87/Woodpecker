import psutil
import json
import time

from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.logging.sender import Sender

__author__ = 'Stefano'


class Sysmonitor(StoppableThread):

    def __init__(self, str_receiver_url, int_receiver_port, int_polling_interval=10.0):
        super(Sysmonitor, self).__init__()
        self.__initialize(str_receiver_url, int_receiver_port, int_polling_interval)

    def __enter__(self, str_receiver_url, int_receiver_port, int_polling_interval=10.0):
        self.__initialize(str_receiver_url, int_receiver_port, int_polling_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __initialize(self, str_receiver_url, int_receiver_port, int_polling_interval):
        self.sender = Sender(str_receiver_url, int_receiver_port, 'UDP')
        self.polling_interval = int_polling_interval

    @staticmethod
    def send_sysmonitor_info():
        tpl_memory = psutil.virtual_memory()
        dic_payload = {
            'CPUperc': psutil.cpu_percent(interval=0.1),
            'memoryUsed': tpl_memory.total - tpl_memory.available,
            'memoryAvail': tpl_memory.available,
            'memoryPerc': tpl_memory.percent
        }

        # self.sender.send('sysmonitor', json.dumps(dic_payload))
        print json.dumps(dic_payload)

    def run(self):
        while True:
            self.send_sysmonitor_info()
            time.sleep(self.polling_interval)

import psutil
import json
from woodpecker.logging.sender import Sender

__author__ = 'Stefano'


class Sysmonitor(object):

    def __init__(self, str_receiver_url, int_receiver_port):
        self.__initialize(str_receiver_url, int_receiver_port)

    def __enter__(self, str_receiver_url, int_receiver_port):
        self.__initialize(str_receiver_url, int_receiver_port)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __initialize(self, str_receiver_url, int_receiver_port):
        self.sender = Sender(str_receiver_url, int_receiver_port, 'UDP')

    def send_sysmonitor_info(self):
        tpl_memory = psutil.virtual_memory()
        dic_payload = {
            'CPUperc': psutil.cpu_percent(interval=0.1),
            'memoryUsed': tpl_memory.total - tpl_memory.available,
            'memoryAvail': tpl_memory.available,
            'memoryPerc': tpl_memory.percent
        }

        self.sender.send('sysmonitor', json.dumps(dic_payload))
        return dic_payload

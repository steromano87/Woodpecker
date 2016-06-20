import psutil
import json
import time

import woodpecker.misc.utils as utils

from woodpecker.misc.stoppablethread_old import StoppableThread
from woodpecker.logging.sender import Sender

__author__ = 'Stefano'


class Sysmonitor(StoppableThread):

    def __init__(self,
                 str_receiver_url,
                 int_receiver_port,
                 int_polling_interval=10.0,
                 str_host_type='remote',
                 bool_debug=False):
        super(Sysmonitor, self).__init__()
        self.__initialize(str_receiver_url,
                          int_receiver_port,
                          int_polling_interval, str_host_type,
                          bool_debug)

    def __enter__(self,
                  str_receiver_url,
                  int_receiver_port,
                  int_polling_interval=10.0,
                  str_host_type='remote',
                  bool_debug=False):
        self.__initialize(str_receiver_url,
                          int_receiver_port,
                          int_polling_interval,
                          str_host_type,
                          bool_debug)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __initialize(self,
                     str_receiver_url,
                     int_receiver_port,
                     int_polling_interval,
                     str_host_type,
                     bool_debug):
        self.sender = Sender(str_receiver_url, int_receiver_port, 'UDP')
        self.polling_interval = int_polling_interval
        self.cpu_percent = CpuPercent()
        self.host_type = str_host_type
        self.debug = bool_debug

    def send_sysmonitor_info(self):
        tpl_memory = psutil.virtual_memory()
        dic_payload = {
            'hostName': utils.get_ip_address(),
            'timestamp': utils.get_timestamp(),
            'hostType': self.host_type,
            'CPUperc': self.cpu_percent.update(),
            'memoryUsed': tpl_memory.total - tpl_memory.available,
            'memoryAvail': tpl_memory.available,
            'memoryPerc': tpl_memory.percent
        }

        self.sender.send('sysmonitor', dic_payload)

        # Prints info on console only if in debug mode
        if self.debug:
            print json.dumps(dic_payload)

    def run(self):
        while True:
            self.send_sysmonitor_info()
            time.sleep(self.polling_interval)


class CpuPercent:
    """Keep track of cpu usage."""

    def __init__(self):
        self.last = psutil.cpu_times()

    def update(self):
        """CPU usage is specific CPU time passed divided by total CPU time passed."""

        last = self.last
        current = psutil.cpu_times()

        total_time_passed = sum([current.__dict__.get(key, 0) - last.__dict__.get(key, 0)
                                 for key in current.__dict__.iterkeys()])

        # only keeping track of system and user time
        sys_time = current.system - last.system
        usr_time = current.user - last.user

        self.last = current

        if total_time_passed > 0:
            sys_percent = 100 * sys_time / total_time_passed
            usr_percent = 100 * usr_time / total_time_passed
            return round(sys_percent + usr_percent, 2)
        else:
            return 0

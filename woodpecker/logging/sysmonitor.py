import psutil
import time

import woodpecker.misc.utils as utils

from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.logging.log import Log
from woodpecker.options import Options

__author__ = 'Stefano'


class Sysmonitor(StoppableThread):

    def __init__(self, str_host_type, **kwargs):
        super(Sysmonitor, self).__init__()

        # Options
        self._options = kwargs.get('options', Options())

        # Internal sender
        self._log = kwargs.get('log', Log())

        # Polling interval
        self.polling_interval = kwargs.get('sysmonitor_polling_interval',
                                           self._options.get('logging', 'sysmonitor_polling_interval'))

        # CPU Percent class
        self.cpu_percent = CpuPercent()

        # Host type (spawner or controller)
        self.host_type = str_host_type

    def __enter__(self, **kwargs):
        self.__init__(**kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

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

        self._log.append_to('sysmonitor', dic_payload)

    def run(self):
        while True:
            if not self.is_marked_for_stop():
                self.send_sysmonitor_info()
                time.sleep(self.polling_interval)
            else:
                break


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

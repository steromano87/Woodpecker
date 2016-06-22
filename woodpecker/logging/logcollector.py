import SocketServer
import json
import socket

from woodpecker.logging.dbwriter import DBWriter
from woodpecker.misc.stoppablethread_old import StoppableThread

__author__ = 'Stefano'


class LogCollector(SocketServer.BaseRequestHandler):

    def setup(self):
        self.dbwriter = DBWriter(self.server.results_file_path)

    def handle(self):
        str_message = self.request[0].strip()
        dic_message = json.loads(str_message)
        dic_payload = dic_message.get('payload', {})

        if dic_message.get('dataType') == 'transactionStart':
            self.dbwriter.write_transaction_start(dic_payload)
        elif dic_message.get('dataType') == 'transactionEnd':
            self.dbwriter.write_transaction_end(dic_payload)
        elif dic_message.get('dataType') == 'request':
            self.dbwriter.write_request(dic_payload)
        elif dic_message.get('dataType') == 'spawns':
            self.dbwriter.write_spawns_info(dic_payload)
        elif dic_message.get('dataType') == 'sysmonitor':
            self.dbwriter.write_sysmonitor_info(dic_payload)
        elif dic_message.get('dataType') == 'message':
            self.dbwriter.write_message(dic_payload)


class LogCollectorThread(StoppableThread):
    def __init__(self, str_results_file_path, str_ip_address=socket.gethostname(), int_port=7878):
        super(LogCollectorThread, self).__init__()
        self.server = SocketServer.UDPServer((str_ip_address, int_port), LogCollector)
        self.server.results_file_path = str_results_file_path

    def run(self):
        self.server.serve_forever()

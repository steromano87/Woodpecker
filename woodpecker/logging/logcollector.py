import SocketServer
import json

from woodpecker.logging.dbwriter import DBWriter

__author__ = 'Stefano'


class LogCollector(SocketServer.BaseRequestHandler):

    def setup(self):
        self.dbwriter = DBWriter(self.server.result_file_path)

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

if __name__ == '__main__':
    obj_server = SocketServer.UDPServer(('localhost', 7878), LogCollector)
    obj_server.result_file_path = "D:/Data/Varie/Programmi Python/Woodpecker/tests/results.sqlite"
    obj_server.serve_forever()

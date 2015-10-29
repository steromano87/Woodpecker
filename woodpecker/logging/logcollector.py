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

        if dic_message.get('logType') == 'transactionStart':
            self.dbwriter.write_transaction_start(dic_payload)
        elif dic_message.get('logType') == 'transactionEnd':
            self.dbwriter.write_transaction_end(dic_payload)
        elif dic_message.get('logType') == 'request':
            self.dbwriter.write_request(dic_payload)
        elif dic_message.get('logType') == 'spawns':
            self.dbwriter.write_spawns_info(dic_payload)
        elif dic_message.get('logType') == 'sysmonitor':
            self.dbwriter.write_sysmonitor_info(dic_payload)
        elif dic_message.get('logType') == 'message':
            self.dbwriter.write_message(dic_payload)

if __name__ == '__main__':
    obj_server = SocketServer.UDPServer(('localhost', 7777), LogCollector)
    obj_server.result_file_path = "D:/Data/Varie/Programmi Python/Woodpecker/tests/results.sqlite"
    obj_server.serve_forever()

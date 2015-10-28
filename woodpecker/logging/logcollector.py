import SocketServer
import json

from woodpecker.logging.dbwriter import DBWriter

__author__ = 'Stefano'


class LogCollector(SocketServer.StreamRequestHandler):

    def __init__(self, request, client_address, server):
        self.dbwriter = DBWriter('testDB.sqlite')
        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        str_message = self.rfile.readline().strip()
        dic_message = json.loads(str_message)

        if dic_message.get('logType') == 'transactionStart':
            self.dbwriter.write_transaction_start(dic_message.get('payload', {}))
        elif dic_message.get('logType') == 'transactionEnd':
            self.dbwriter.write_transaction_end(dic_message.get('payload', {}))
        elif dic_message.get('logType') == 'request':
            self.dbwriter.write_request(dic_message.get('payload', {}))
        elif dic_message.get('logType') == 'spawns':
            self.dbwriter.write_spawns_info(dic_message.get('payload', {}))
        elif dic_message.get('logType') == 'sysmonitor':
            self.dbwriter.write_sysmonitor_info(dic_message.get('payload', {}))

if __name__ == '__main__':
    obj_server = SocketServer.TCPServer(('localhost', 7777), LogCollector)
    obj_server.serve_forever()

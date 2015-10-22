import SocketServer
import json

from woodpecker.logging.dbwriter import DBWriter

__author__ = 'Stefano'


class LogCollector(SocketServer.StreamRequestHandler):

    def setup(self):
        pass

    def handle(self):
        str_payload = self.rfile.readline().strip()
        obj_payload = json.loads(str_payload)

        if obj_payload['logType'] == 'transaction':
            pass

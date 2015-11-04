import socket
import json

__author__ = 'Stefano.Romano'


class Sender(object):

    def __init__(self, str_receiver_url, int_receiver_port, str_protocol):
        self.__initialize(str_receiver_url, int_receiver_port, str_protocol)

    def __enter__(self, str_receiver_url, int_receiver_port, str_protocol):
        self.__initialize(str_receiver_url, int_receiver_port, str_protocol)

    def __initialize(self, str_receiver_url, int_receiver_port, str_protocol):
        self.receiver_url = str_receiver_url
        self.receiver_port = int_receiver_port
        self.protocol = str_protocol
        self.socket = None

    def send(self, str_data_type, dic_data):
        dic_payload = {'dataType': str_data_type, 'payload': dic_data}
        str_payload = json.dumps(dic_payload)

        # Connects and send data
        try:
            if self.protocol == 'TCP':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.receiver_url, self.receiver_port))
                int_sent_bytes = self.socket.send(str_payload)
            elif self.protocol == 'UDP':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                int_sent_bytes = self.socket.sendto(str_payload, (self.receiver_url, self.receiver_port))
            else:
                self.socket = None
                int_sent_bytes = -1
        finally:
            self.socket.close()

        return int_sent_bytes

import socket
import json

__author__ = 'Stefano.Romano'


class Sender(object):

    def __init__(self, str_receiver_url, int_receiver_port):
        self.receiver_url = str_receiver_url
        self.receiver_port = int_receiver_port

        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.receiver_url, self.receiver_port))

    def send(self, str_data_type, dic_data):
        dic_payload = {'dataType': str_data_type, 'payload': dic_data}
        str_payload = json.dumps(dic_payload)
        return self.socket.send(str_payload)

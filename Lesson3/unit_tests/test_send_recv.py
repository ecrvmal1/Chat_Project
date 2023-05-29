import sys
import os
import unittest
import json
sys.path.append(os.path.join(os.getcwd(), '..'))

from common.server_utils import get_message, send_message


class Test_Sock():
    def __init__(self):
        self.sock_sent_msg = None
        self.sock_received_msg = {'test': "test message"}

    def recv(self, packet_length):
        json_obj = json.dumps(self.sock_received_msg)
        return json_obj.encode('utf-8')

    def send(self, byte_string):
        json_string = byte_string.decode('utf-8')
        self.sock_sent_msg = json.loads(json_string)


class TestSendRcv(unittest.TestCase):

    def test_send_msg(self):
        sock = Test_Sock()
        test_message = {'response': 200}
        send_message(sock, test_message)
        self.assertEqual(sock.sock_sent_msg, test_message)

    def test_get_message(self):
        sock = Test_Sock()
        got_message = get_message(sock)
        self.assertEqual(sock.sock_received_msg, got_message)


if __name__ == '__main__':
    unittest.main()









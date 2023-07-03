### Tests for client utiils ###

import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '../Lesson3'))
from client.client_utils import get_ip_address, presence_msg, process_ans, client_connection, user_msg


class TestClass(unittest.TestCase):

    def test_command_line_address_1(self):
        commandline = ['-a', '127.0.0.1', '-p', '7777']
        self.assertEqual(get_ip_address(commandline), '127.0.0.1')

    # Это не работает, в функции стоит sys.exit(1), ругается на эту команду

    def test_command_line_address_2(self):
        commandline = ['-a']
        with self.assertRaises(SystemExit):
            get_ip_address(commandline)

    def test_command_line_address_3(self):
        commandline = []
        self.assertEqual(get_ip_address(commandline), None)

    def test_presence_msg_1(self):
        result ={'action': 'presence', 'time': 0.001, 'type': 'status',
                   'user': {"account_name": 'Guest', "status": "connected" }}
        test = presence_msg()
        test['time'] = 0.001
        self.assertEqual(test, result)

    def test_presence_msg_2(self):
        result ={'action': 'presence', 'time': 0.001, 'type': 'status',
                   'user': {"account_name": 'User', "status": "connected" }}
        test = presence_msg('User')
        test['time'] = 0.001
        self.assertEqual(test, result)

    def test_process_ans_1(self):
        message = {'answer': 200}
        with self.assertRaises(ValueError):
            process_ans(message)

    def test_process_ans_2(self):
        message = {'response': "ABC"}
        with self.assertRaises(ValueError):
            process_ans(message)

    def test_process_ans_200(self):
        message = {'response': 200}
        self.assertEqual(process_ans(message), '200: OK')

    def test_process_ans_400(self):
        message = {'response': 400}
        self.assertEqual(process_ans(message), '400: Error')

    def test_client_connection_if_server_down(self):
        server_ip = '127.0.0.1'
        server_port = 7777
        with self.assertRaises(SystemExit):
            client_connection(server_ip, server_port)


    def test_user_message_1(self):
        print('\n test "user_msg:"')
        result = user_msg()
        # {'action': "msg", 'time': time.time(), 'to': user_to, 'from': 'Guest',
        #  'encoding': ENCODING, 'message': user_message}
        test = "action" in result \
            and result["action"] == 'msg'  \
            and "to" in result  \
            and isinstance(result['to'], str) \
            and "from" in result \
            and isinstance(result['from'], str) \
            and "encoding" in result \
            and "message" in result \
            and isinstance(result['message'], str)
        self.assertTrue(test)


if __name__ == '__main__':
    unittest.main()

### Tests for client utiils ###

import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '../Lesson3'))
from server.server_utils import get_ip_address, process_incoming_message
from server.server_variables import RESPONSE, ACTION, PRESENCE, TIME


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

    def test_process_incoming_message_1(self):
        test_message = {ACTION: PRESENCE,
                        TIME: 0.1,
                        'user':
                            {'account_name': 'Guest'}
                        }
        test_response = {'response': {RESPONSE: 200}}
        self.assertEqual(process_incoming_message(test_message), test_response)

    def test_process_incoming_message_2(self):
        test_message = {ACTION: 'msg',
                        TIME: 0.1,
                        'to': 'user2',
                        'from': 'Guest'
                        }
        test_response = {'response': {RESPONSE: 201}}
        self.assertEqual(process_incoming_message(test_message), test_response)

    def test_process_incoming_message_3(self):
        test_message = {ACTION: 'quit'}
        test_response = {'response': {RESPONSE: 202}, 'quit': " "}
        self.assertEqual(process_incoming_message(test_message), test_response)

    def test_process_incoming_message_4(self):
        test_message = {ACTION: "something",
                        TIME: 0.1,
                        'user':
                            {'account_name': 'Guest'}
                        }
        test_response = {'response': {'response': 400,
                                      'error': 'Bad Request'
                                      }}
        self.assertEqual(process_incoming_message(test_message), test_response)

    def test_process_incoming_message_5(self):
        test_message = {ACTION: PRESENCE,
                        "times": 0.1,
                        'user':
                            {'account_name': 'Guest'}
                        }
        test_response = {'response': {'response': 400,
                                      'error': 'Bad Request'
                                      }}
        self.assertEqual(process_incoming_message(test_message), test_response)

    def test_process_incoming_message_6(self):
        test_message = {ACTION: PRESENCE,
                        TIME: 0.1,
                        'user':
                            {'account_name': 'USER'}
                        }
        test_response = {'response': {'response': 400,
                                      'error': 'Bad Request'
                                      }}
        self.assertEqual(process_incoming_message(test_message), test_response)





    def test_process_incoming_message_6(self):
        test_message = "something_else"
        test_response = {'response':
                             {'response': 400,
                              'error': 'Bad Request'
                              }}
        self.assertEqual(process_incoming_message(test_message), test_response)





if __name__ == "__main__":
    unittest.main()

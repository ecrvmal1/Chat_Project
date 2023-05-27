from socket import *
import sys
import json
import time

from common.client_variables import DEFAULT_CLIENT_PORT, DEFAULT_CLIENT_IP_ADDRESS, CLIENT_NAME

from common.client_utils import get_ip_address, get_port, client_connection, terminal_info, \
    presence_msg, send_message, process_ans, get_message, client_disconnection, user_msg

transport = None
connection = False
message = ""

if __name__ == '__main__':

    client_ip_address = get_ip_address(sys.argv)
    if client_ip_address is None:
        client_ip_address = DEFAULT_CLIENT_IP_ADDRESS

    client_port = get_port(sys.argv)
    if client_port is None:
        client_port = DEFAULT_CLIENT_PORT

    print(f'port : {client_port} \n'
          f'IP Address : {client_ip_address}\n')
    message = ""
    while True:
        action = terminal_info(message)
        if action == 1:
            connection, transport = client_connection(client_ip_address, client_port)
            msg = presence_msg()
            send_message(transport, msg)
            try:
                message = process_ans(get_message(transport))
                client_disconnection(transport)
            except (ValueError, json.JSONDecodeError):
                message = 'Not able to decode from SERVER'

        elif action == 2:
            connection, transport = client_connection(client_ip_address, client_port)
            msg = user_msg()
            send_message(transport, msg)
            try:
                message = process_ans(get_message(transport))
                client_disconnection(transport)
            except (ValueError, json.JSONDecodeError):
                message = 'Not able to decode from SERVER'

        elif action == 3:
            if connection is True:
                connection, transport = client_connection(client_ip_address, client_port)
                msg = {'action': 'quit'}
                send_message(transport, msg)
                try:
                    message = process_ans(get_message(transport))
                    client_disconnection(transport)
                except (ValueError, json.JSONDecodeError):
                    message = 'Not able to decode from SERVER'

        elif action == 4:
            pass
        elif action == 5:
            pass
        elif action == 6:
            print('******************************')
            print('        program closing       ')
            print('******************************')
            time.sleep(2)
            sys.exit(0)
        else:
            message = " Please enter menu item 1...6"








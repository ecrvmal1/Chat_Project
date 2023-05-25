from socket import *
import sys
import json


from common.server_variables import DEFAULT_SERVER_IP_ADDRESS, DEFAULT_SERVER_PORT, MAX_CONNECTIONS

from common.server_utils import get_ip_address, get_port, process_incoming_message, send_message, \
    get_message

def main():
    server_ip_address = get_ip_address(sys.argv)
    if server_ip_address is None:
        server_ip_address = DEFAULT_SERVER_IP_ADDRESS

    server_port = get_port(sys.argv)
    if server_port is None:
        server_port = DEFAULT_SERVER_PORT

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((server_ip_address, server_port))

    # Listen the port
    transport.listen(MAX_CONNECTIONS)


    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = process_incoming_message(message_from_client)
            send_message(client, response)
            # client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()

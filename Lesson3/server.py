import socket
import sys
import json
import logging
from datetime import datetime

import log.server_log_config
from common.server_variables import DEFAULT_SERVER_IP_ADDRESS, DEFAULT_SERVER_PORT, MAX_CONNECTIONS

from common.server_utils import get_ip_address, get_port, process_incoming_message, send_message, \
    get_message


def main():
    LOGGER = logging.getLogger('server_logger')

    server_ip_address = get_ip_address(sys.argv)
    if server_ip_address is None:
        server_ip_address = DEFAULT_SERVER_IP_ADDRESS
    LOGGER.info(f'Server got IP ADDRESS {server_ip_address}')

    server_port = get_port(sys.argv)
    if server_port is None:
        server_port = DEFAULT_SERVER_PORT
    LOGGER.info(f'Server got TCP Port {server_port}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((server_ip_address, server_port))

    while True:
    # Listen the port
        transport.listen(MAX_CONNECTIONS)
        client, client_address = transport.accept()
        # print(f'client from IP {client_address} connected')
        LOGGER.info(f'client from IP {client_address} connected')

        try:
            message_from_client = get_message(client)
            # print(f'{datetime.now()} message_from_client: {message_from_client}')
            LOGGER.info(f'message_from_client: {message_from_client}')
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            actions = process_incoming_message(message_from_client)
            # print (f'processing incoming message : {actions}')
            if 'response' in actions:
                try:
                    send_message(client, actions['response'])
                except KeyError as e:
                    # print(f'Error {e}')
                    LOGGER.error(f'Send_Message_error {e}')
            if 'quit' in actions:
                # print(f' Client {client} disconnected')
                LOGGER.info(f'Client Disconnected')
            client.close()
        except (ValueError, json.JSONDecodeError):
            # print('Принято некорретное сообщение от клиента.')
            LOGGER.error(f'Got incorrect message from Client, Client will be closed')
            client.close()


if __name__ == '__main__':
    main()

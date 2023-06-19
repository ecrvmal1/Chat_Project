import socket
import sys
import json
import logging
import threading
import time

import log.client_log_config
from common.errors import ServerError, ReqFieldMissingError
from deco_log import log


from common.client_utils import arg_parser, send_message, display_incoming_message, process_response, \
    create_message_presence, get_message, main_menu

LOGGER = logging.getLogger('client_logger')


def main():
    print('********** CHAT CLIENT RUNNING *************' )
    """Загружаем параметы коммандной строки"""
    server_address, server_port, client_username = arg_parser()
    if not client_username:
        client_username = input('Please enter your username: ')

    LOGGER.info(
        f'Client runs , Server IP address : {server_address}, '
        f'Port number : {server_port}, Usernabe: {client_username}')
    print(
        f'Client runs , Server IP address : {server_address}, '
        f'Port number : {server_port}, Usernabe: {client_username}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_message_presence(client_username))
        answer = process_response(get_message(transport))
        LOGGER.info(f'Connection to server established,  Server response: {answer}')
        print(f'Connection to server established,  Server response: {answer}')
    except json.JSONDecodeError:
        LOGGER.error('Not able to decode JSON string.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'Server returns ERROR at connection attempt: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'Missing fields in server response {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Server not available {server_address}:{server_port}, '
            f'Server refused correction request')
        sys.exit(1)

    else:
        receiver = threading.Thread(target=display_incoming_message, args=(transport, client_username))
        receiver.daemon = True
        receiver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        user_interface = threading.Thread(target=main_menu, args=(transport, client_username))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Threads run')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break




if __name__ == '__main__':
    main()





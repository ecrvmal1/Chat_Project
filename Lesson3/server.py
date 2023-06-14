"""  THE SERVER SCRIPT """

import socket
import logging
import select
import sys
import time
import threading

sys.path.append('../')
import log.server_log_config
from common.server_variables import DEFAULT_SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, \
    FROM, TO, SENDER, PRESENCE, RESPONSE, ERROR, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, RESPONSE_400


from common.server_utils import arg_parser, process_client_message, get_message, send_message, \
    server_service
from deco_log import log

from common.errors import IncorrectDataRecivedError

LOGGER = logging.getLogger('server_logger')


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    LOGGER.info(
        f'Server runs, listen port: {listen_port}, '
        f'incoming IP addresses: {listen_address}. '
        f'In case incoming IP address is not defined, connections are possible from any IP address.')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # список клиентов , очередь сообщений
    clients = list()
    messages = list()
    user_list = dict()

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    user_interface = threading.Thread(target=server_service)
    user_interface.daemon = True
    user_interface.start()
    LOGGER.debug('Threads run')

    print('For exit from server press "q" key')

    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Client connected  {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass


        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            print('recv_data_lst', recv_data_lst)
            for client in recv_data_lst:
                try:
                    # print(f'trying get message from {client_with_message}')
                    new_message = get_message(client)
                    process_client_message(new_message, messages, client, clients, user_list)
                except ConnectionResetError:
                    LOGGER.info(f'Client {client.getpeername()}  disconnected ')
                    clients.remove(client)
                except IncorrectDataRecivedError:
                    LOGGER.info(f'Got Incorrect data from client {client.getpeername()} ')


        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        # print(f'messages : {messages}')

        if messages and send_data_lst:
            # print(f'messages : {messages}')
            new_message = {
                ACTION: MESSAGE,
                FROM: messages[0][FROM],
                TO: messages[0][TO],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][MESSAGE_TEXT]
            }
            destination_name = messages[0][TO]
            if destination_name not in user_list.keys():
                sender_sock = user_list[messages[0][FROM]]
                send_message(sender_sock, RESPONSE_400)
                del messages[0]
            else:
                destination_sock = user_list[destination_name]
                del messages[0]
                try:
                    send_message(destination_sock, new_message)
                except OSError:
                    LOGGER.info(f'Client {destination_sock.getpeername()} disconnected from server.')
                    clients.remove(destination_sock)


if __name__ == '__main__':
    main()

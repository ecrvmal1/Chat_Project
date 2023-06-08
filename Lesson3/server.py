"""  THE SERVER  """

import socket
import logging
import select
import sys
import time

sys.path.append('../')
import log.server_log_config
from common.server_variables import DEFAULT_SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, \
    ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT


from common.server_utils import arg_parser, process_client_message, get_message, send_message
from deco_log import log

from common.errors import IncorrectDataRecivedError

LOGGER = logging.getLogger('server_logger')


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # список клиентов , очередь сообщений
    clients = []
    messages = []

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера
    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соедение с клиентом {client_address}')
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
            for recv_data in recv_data_lst:
                try:
                    # print(f'trying get message from {client_with_message}')
                    new_message = get_message(recv_data)
                    process_client_message(new_message, messages, recv_data)
                except ConnectionResetError:
                    LOGGER.info(f'Клиент {recv_data.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(recv_data)
                except IncorrectDataRecivedError:
                    LOGGER.info(f'Got Incorrect data from client {recv_data.getpeername()} ')


        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        # print(f'messages : {messages}')
        if send_data_lst:
            print('send_data_lst', send_data_lst)
        if messages and send_data_lst:
            print(f'messages : {messages}')
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except OSError:
                    LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()

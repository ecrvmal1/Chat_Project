"""  THE SERVER SCRIPT """

import socket
import logging
import select
import sys
import time
import threading
import os

sys.path.append('../')
import log.server_log_config
from Lesson3.common.server_variables import DEFAULT_SERVER_PORT, MAX_CONNECTIONS, ACTION, TIME, EXIT, \
    FROM, TO, SENDER, PRESENCE, RESPONSE, ERROR, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, RESPONSE_400


from common.server_utils import arg_parser, get_message, send_message
from deco_log import log

from common.errors import IncorrectDataRecivedError
from descriptors import Port
from metaclasses import ServerMaker

LOGGER = logging.getLogger('server_logger')


def server_service():
    print_command_help()
    while True:
        command = input('')
        if command == 'q':
            print('Exiting Server after operator command')
            LOGGER.info('Exiting Server after operator command')
            time.sleep(1.0)
            os._exit(0)
            # sys.exit()


def print_command_help():
    """Функция выводящяя справку по использованию"""
    print(' Please enter command "q" for exit from server:')


class Server(metaclass=ServerMaker):

    port = Port()

    def __init__(self, listen_address, listen_port):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.clients = list()
        self.messages = list()
        self.user_list = dict()
        self.sock = None

        LOGGER.info(
            f'Server runs, listen port: {listen_port}, '
            f'incoming IP addresses: {listen_address}. '
            f'In case incoming IP address is not defined, connections are possible from any IP address.')

    def init_sock(self):
        """
        Preparation of socket
        :return: socket
        """
        LOGGER.info(f'Server runs, Connection port:  {self.listen_port} '
                    f'Connection address : {self.listen_address}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.listen_address, self.listen_port))
        transport.settimeout(0.5)

        self.sock = transport

        # Listen ports
        self.sock.listen(MAX_CONNECTIONS)

        user_interface = threading.Thread(target=server_service)
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Threads run')

        print('For exit from server press "q" key')

    @log
    def main_loop(self):
        # Основной цикл программы сервера
        print('For exit from server press "q" key')

        self.init_sock()

        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Client connected  {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
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
                        self.process_client_message(new_message, client)
                    except ConnectionResetError:
                        LOGGER.info(f'Client {client.getpeername()}  disconnected ')
                        self.clients.remove(client)
                    except IncorrectDataRecivedError:
                        LOGGER.info(f'Got Incorrect data from client {client.getpeername()} ')


            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            # print(f'messages : {messages}')

            if self.messages and send_data_lst:
                # print(f'messages : {messages}')
                new_message = {
                    ACTION: MESSAGE,
                    FROM: self.messages[0][FROM],
                    TO: self.messages[0][TO],
                    TIME: time.time(),
                    MESSAGE_TEXT: self.messages[0][MESSAGE_TEXT]
                }
                destination_name = self.messages[0][TO]
                if destination_name not in self.user_list.keys():
                    sender_sock = self.user_list[self.messages[0][FROM]]
                    send_message(sender_sock, RESPONSE_400)
                    del self.messages[0]
                else:
                    destination_sock = self.user_list[destination_name]
                    del self.messages[0]
                    try:
                        send_message(destination_sock, new_message)
                    except OSError:
                        LOGGER.info(f'Client {destination_sock.getpeername()} disconnected from server.')
                        self.clients.remove(destination_sock)

    @log
    def process_client_message(self, message, client):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
        проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
        :param message:
        :param messages_list:
        :param clients:
        :param client:
        :param user_list:
        :return:
        """
        LOGGER.debug(f'processing message {message} from {client}')
        print(f'processing message {message} from {client}')
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and FROM in message:
            if message[FROM] not in self.user_list.keys():
                self.user_list[message[FROM]] = client
                print(f' user {message[FROM]} added to user_list')
                send_message(client, {RESPONSE: 200})
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and TIME in message \
                and FROM in message \
                and TO in message \
                and MESSAGE_TEXT in message:
            self.messages.append(message)
            # print(f'message added to message_list {self.messages}')
            return
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and FROM in message:
            self.clients.remove(self.user_list[message[FROM]])
            self.user_list[message[FROM]].close()
            del self.user_list[message[FROM]]
            return
        # Иначе отдаём Bad request
        else:
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            })
            print(f'sent error message to {client}')
            return


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    # user_interface = threading.Thread(target=server_service)
    # user_interface.daemon = True
    # user_interface.start()
    # LOGGER.debug('Threads run')

    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()

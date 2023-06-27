"""  THE SERVER SCRIPT """

import socket
import logging
import select
import sys
import threading
import os

from common.server_variables import *
from common.server_utils import arg_parser, get_message, send_message
from deco_log import log

from common.errors import IncorrectDataRecivedError
from descriptors import Port
from server_database import *

LOGGER = logging.getLogger('server_logger')

new_connection = False
# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
connflag_lock = threading.Lock()


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


# class Server(metaclass=ServerMaker):
class Server(threading.Thread):

    listen_port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.database = database
        self.clients = list()
        self.messages = list()
        self.user_list = dict()     # [{username: client},   ]
        self.sock = None
        super().__init__()

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


    def run(self):
        # Основной цикл программы сервера

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
                # print(f'client connected :  {client}')
                # print(f'getpeername : {client.getpeername()}')

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError as err:
                LOGGER.error(f'Ошибка работы с сокетами: {err}')


            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                print('recv_data_lst', recv_data_lst)
                for client in recv_data_lst:
                    try:
                        # print(f' trying get message from {client_with_message}')
                        new_message = get_message(client)
                        if new_message:
                            self.process_incoming_message(new_message, client)
                    except OSError:
                        LOGGER.info(f'Client {client.getpeername} disconnected from server')
                        for cl in self.user_list:
                            if self.user_list[cl] == client:
                                self.database.db_user_logout(cl)
                                del self.user_list[cl]
                                self.clients.remove(client)
                                break

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            # print(f'messages : {messages}')

            if self.messages and send_data_lst:
                # print(f'messages : {messages}')
                for message in self.messages:
                    try:
                        self.forward_text_message(message, send_data_lst)
                    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                        LOGGER.info(f'Connection to client "{message[TO]}" lost')
                        self.clients.remove(self.user_list[message[TO]])
                        del self.user_list[message[TO]]
                        self.database.db_user_logout(message[TO])
                self.messages.clear()

    def process_incoming_message(self, message, client):
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

        # ACTION : PRESENCE
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and FROM in message:
            if message[FROM] not in self.database.db_active_users_list():
                self.user_list[message[FROM]] = client
                print(f' user {message[FROM]} added to user_list')
                client_ip, client_port = client.getpeername()
                self.database.db_user_login(message[FROM], client_ip, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        # MESSAGE
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
            self.database.db_user_logout(message[FROM])
            LOGGER.info(f'client {message[FROM]} disconnected from server correctly')
            with connflag_lock:
                new_connection = True
            return

        # ACTION RESPONSE
        elif ACTION in message \
                and message[ACTION] == RESPONSE \
                and RESPONSE in message:
            print(f'message response : {message[RESPONSE]}')

        # ACTION : GET_CONTACTS
        elif ACTION in message \
                and message[ACTION] == GET_CONTACTS \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            response = RESPONSE_202
            response['contact_list'] = self.database.db_contacts_list(message[FROM])
            send_message(client, response)

        # ACTION ADD_CONTACT
        elif ACTION in message \
                and message[ACTION] == ADD_CONTACT \
                and CONTACT in message \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            self.database.add_contact(message[FROM], message[CONTACT])
            send_message(client, RESPONSE_200)

        # ACTION REMOVE_CONTACT
        elif ACTION in message \
                and message[ACTION] == REMOVE_CONTACT \
                and FROM in message \
                and CONTACT in message \
                and self.user_list[message[FROM]] == client:
            self.database.db_contacts_remove(message[FROM], message[CONTACT])
            send_message(client, RESPONSE_200)

            # Если это запрос известных пользователей
        # ACTION USERS_REQUEST
        elif ACTION in message \
                and message[ACTION] == 'get_users' \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            response = RESPONSE_202
            response['user_list'] = [user.name for user in self.database.db_all_users_list()]
            send_message(client, response)

            # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect Query'
            send_message(client, response)
            return

    def forward_text_message(self, message, listen_socks):
        print(f'forward test message {message}')
        if message[TO] in self.user_list \
                and self.user_list[message[TO]] in listen_socks:
            send_message(self.user_list[message[TO]], message)
            LOGGER.info(f'The message  forwarded to user "{message[TO]}" from user "{message[FROM]}".')
        elif message[TO] in self.user_list and self.user_list[message[TO]] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(
                f'User "{message[TO]}" has not registered, Message can not be sent.')


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    # user_interface = threading.Thread(target=server_service)
    # user_interface.daemon = True
    # user_interface.start()
    # LOGGER.debug('Threads run')
    database = ServerStorage()

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    print_help()

    # ----------------------- Main  Cycle ------------------------:
    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            os._exit(0)
        elif command == 'users':
            for user in sorted(database.db_all_users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.db_active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.db_login_history_list(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()

"""  THE SERVER SCRIPT """
import configparser
import socket
import logging
import select
import sys
import threading
import os
from json import JSONDecodeError

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from common.server_variables import *
from common.server_utils import arg_parser, get_message, send_message, pid_used_port
from deco_log import log

from common.errors import IncorrectDataRecivedError
from descriptors import Port
from server_database import *
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow

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
        try:
            transport.bind((self.listen_address, self.listen_port))
        except OSError:
            pid_no = pid_used_port(self.listen_port)
            time.sleep(1)
            sys.exit(0)

        transport.settimeout(0.5)

        self.sock = transport
        # Listen ports
        self.sock.listen()

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
                pass
            # print(f'recv_data_lst : {recv_data_lst}')

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client in recv_data_lst:
                    try:
                        # print(f' trying get message from {client_with_message}')
                        new_message = get_message(client)
                        if new_message:
                            self.process_incoming_message(new_message, client)
                    except IncorrectDataRecivedError as err:
                        print(f'Message decoding Error : {err}')
                        continue
                    except (OSError, JSONDecodeError):
                        LOGGER.info(f'Client {client.getpeername} disconnected from server')
                        usr_to_del =""
                        for usr in self.user_list:
                            if self.user_list[usr] == client:
                                usr_to_del= usr
                        self.database.db_user_logout(usr_to_del)
                        self.clients.remove(client)
                        del self.user_list[usr_to_del]
                    continue

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
                    try:
                        send_message(self.user_list[message[FROM]], RESPONSE_200)
                    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                        LOGGER.info(f'Connection to client "{message[FROM]}" lost')
                        self.clients.remove(self.user_list[message[FROM]])
                        del self.user_list[message[FROM]]
                        self.database.db_user_logout(message[FROM])
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

        global new_connection
        LOGGER.debug(f'processing message {message} from {client}')
        print(f'processing message {message} from {client}')


        # with sock_lock:
        # ACTION : PRESENCE
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and FROM in message:
            if message[FROM] not in self.user_list.keys():
                self.user_list[message[FROM]] = client
                print(f' user {message[FROM]} added to user_list')
                client_ip, client_port = client.getpeername()
                self.database.db_user_login(message[FROM], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with connflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = f'username {message[FROM]} is already in use'
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
            self.database.db_message_register_update(message)
            self.database.db_message_counter_update(message)
            # print(f'message added to message_list {self.messages}')
            return

        # ACTION EXIT
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and FROM in message \
                and message[FROM] in self.user_list.keys():
            print(f'exiting {message[FROM]}')
            self.clients.remove(self.user_list[message[FROM]])
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
            print(f'processing contact list for {message[FROM]}')
            c_list = self.database.db_contacts_list(message[FROM])
            print(f'contact list : {c_list}')
            response['contact_list'] = c_list
            if "user_list" in response:
                del response["user_list"]
            send_message(client, response)

        # ACTION ADD_CONTACT
        elif ACTION in message \
                and message[ACTION] == ADD_CONTACT \
                and CONTACT in message \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            try:
                self.database.db_contacts_add(message[FROM], message[CONTACT])
                send_message(client, RESPONSE_200)
            except ValueError as err:
                response = RESPONSE_400
                response['error'] = str(err)
                send_message(client, response)

        # ACTION REMOVE_CONTACT
        elif ACTION in message \
                and message[ACTION] == REMOVE_CONTACT \
                and FROM in message \
                and CONTACT in message \
                and self.user_list[message[FROM]] == client:
            self.database.db_contacts_remove(message[FROM], message[CONTACT])
            send_message(client, RESPONSE_200)

            # Если это запрос известных пользователей
        # ACTION GET_USERS
        elif ACTION in message \
                and message[ACTION] == 'get_users' \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            response = RESPONSE_202
            response['user_list'] = [user.name for user in self.database.db_all_users_list()]
            if "contact_list" in response:
                del response["contact_list"]
            send_message(client, response)

            # Else send  Bad request
        else:
            response = {}
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
            print(f" user {message[TO]}  is inactive")
            response = {}
            response = RESPONSE_400
            response[ERROR] = 'User is inactive'
            send_message(self.user_list[message[FROM]], response)
            LOGGER.error(
                f'User "{message[TO]}" has not registered, Message can not be sent.')
        else:
            print(f" user {message[TO]}  is inactive")
            response = RESPONSE_400
            response[ERROR] = 'User is inactive'
            send_message(self.user_list[message[FROM]], response)
            LOGGER.error(
                f'User "{message[TO]}" has not registered, Message can not be sent.')


def main():
    # ------------------  process  server.ini --------------
    config = configparser.ConfigParser()
    config_dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(config_dir_path, 'server.ini')
    config.read(config_file_path)
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser(config['SETTINGS']['Default_ip'], config['SETTINGS']['Default_port'],)

    # user_interface = threading.Thread(target=server_service)
    # user_interface.daemon = True
    # user_interface.start()
    # LOGGER.debug('Threads run')
    config_path = config['SETTINGS']['Database_path']
    config_file = config['SETTINGS']['Database_file']
    if config_path and config_file:
        database_path = os.path.join(config_path, config_file)
    elif config_file :
        database_path = os.path.join(config_path, config_file)
    else:
        database_path = 'server.db3'
    database = ServerStorage(database_path)

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # print_help()

    # ------------------------- GUI ---------------------------
    # Create Graphics environment for server
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # initiate Window
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()


    # Refresh Connections List
    # Check connection flag and refresh window if necessary
    def gui_list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with connflag_lock:
                new_connection = False

    def gui_show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        main_window.active_clients_table.resizeColumnsToContents()
        main_window.active_clients_table.resizeRowsToContents()
        stat_window.show()

    def gui_server_config():
        global config_window
        config_window = ConfigWindow()
        # Создаём окно и заносим в него текущие параметры
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Default_ip'])
        config_window.save_btn.clicked.connect(gui_save_server_config)

    # function Save Settings
    def gui_save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.file_path.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Error', 'Port must be a digit')
        else:
            config['SETTINGS']['ip_address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'Ok', 'Settings has been saved')
            else:
                message.warning(
                    config_window,
                    'Error',
                    'Port must be in range 1024 ... 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(gui_list_update)
    timer.start(1000)

    # link buttons to procedures
    main_window.refresh_button.triggered.connect(gui_list_update)
    main_window.history_button.triggered.connect(gui_show_statistics)
    main_window.config_button.triggered.connect(gui_server_config)

    # run GUI
    server_app.exec_()


    # ----------------------- Main  Cycle ------------------------:
    # ------------------removed since GUI implemented _____________
    # while True:
    #     command = input('Введите комманду: ')
    #     if command == 'help':
    #         print_help()
    #     elif command == 'exit':
    #         os._exit(0)
    #     elif command == 'users':
    #         for user in sorted(database.db_all_users_list()):
    #             print(f'Пользователь {user[0]}, последний вход: {user[1]}')
    #     elif command == 'connected':
    #         for user in sorted(database.db_active_users_list()):
    #             print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
    #     elif command == 'loghist':
    #         name = input('Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
    #         for user in sorted(database.db_login_history_list(name)):
    #             print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
    #     else:
    #         print('Команда не распознана.')


if __name__ == '__main__':
    main()

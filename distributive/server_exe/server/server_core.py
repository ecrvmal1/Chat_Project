import sys
import threading
import logging
import select
import socket
import json
import hmac
import binascii
import os

sys.path.append('../')
from server.server_utils import send_message, get_message
from server.server_variables import *
from common.descriptors import Port
from common.metaclasses import ServerMaker
from server.server_decos import *




from common.errors import IncorrectDataRecivedError, JSONDecodeError
from server.server_decos import login_required
from server.server_utils import send_message, get_message, pid_used_port, print_cli_help




# Загрузка логера
LOGGER = logging.getLogger('server')


class ServerMessageProcessor(threading.Thread):
    '''
    Основной класс сервера. Принимает содинения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    '''
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # База данных сервера
        self.database = database

        # Сокет, через который будет осуществляться работа
        self.sock = None

        # Список подключённых клиентов.
        self.clients = []

        # Сокеты
        self.listen_sockets = None
        self.error_sockets = None

        # Флаг продолжения работы
        self.running = True

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.user_list = dict()

        # Конструктор предка
        super().__init__()

    def run(self):
        '''Метод основной цикл потока.'''
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while self.running:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соедение с ПК {client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, self.listen_sockets, self.error_sockets = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                LOGGER.error(f'Ошибка работы с сокетами: {err.errno}')

            # принимаем сообщения и если ошибка, исключаем клиента.
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
                        LOGGER.info(
                            f'Client {client.getpeername} disconnected from server')
                        usr_to_del = ""
                        for usr in self.user_list:
                            if self.user_list[usr] == client:
                                usr_to_del = usr
                        self.database.db_user_logout(usr_to_del)
                        self.clients.remove(client)
                        del self.user_list[usr_to_del]
                    continue

    def remove_client(self, client):
        '''
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы:
        '''
        LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
        for name in self.user_list:
            if self.user_list[name] == client:
                self.database.user_logout(name)
                del self.user_list[name]
                break
        self.clients.remove(client)
        client.close()

    def init_socket(self):
        '''Метод инициализатор сокета.'''
        LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen(MAX_CONNECTIONS)

    # @login_required
    def forward_text_message(self, message, listen_socks):
        """
        The method forwards text message ot another user
        :param message:
        :param listen_socks:
        :return:
        """
        print(f'forward test message {message}')
        if message[TO] in self.user_list \
                and self.user_list[message[TO]] in listen_socks:
            send_message(self.user_list[message[TO]], message)
            LOGGER.info(
                f'The message  forwarded to user "{message[TO]}" from user "{message[FROM]}".')
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

    # @login_required
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

        LOGGER.debug(f'processing message {message}')
        print(f'processing message {message} from {client}')

        #  ACTION : PRESENCE
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and FROM in message:
            self.authorize_user(message, client)
            return

        # MESSAGE
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and TIME in message \
                and FROM in message \
                and TO in message \
                and MESSAGE_TEXT in message \
                and self.user_list[message[FROM]] in self.clients:
            if message[TO] in self.user_list:
                self.forward_text_message(message, self.listen_sockets)
                self.database.db_message_register_update(message)
                self.database.db_message_counter_update(message)

                try:
                    send_message(self.user_list[message[FROM]], RESPONSE_200)
                except OSError:
                    self.remove_client(self.user_list[message[FROM]])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return

        #  ACTION EXIT
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and FROM in message \
                and message[FROM] in self.user_list.keys():
            print(f'exiting {message[FROM]}')
            self.clients.remove(self.user_list[message[FROM]])
            del self.user_list[message[FROM]]
            self.database.db_user_logout(message[FROM])
            LOGGER.info(
                f'client {message[FROM]} disconnected from server correctly')
            # with connflag_lock:
            #     new_connection = True
            return

        #  ACTION RESPONSE
        elif ACTION in message \
                and message[ACTION] == RESPONSE \
                and RESPONSE in message:
            print(f'message response : {message[RESPONSE]}')

        #  ACTION : GET_CONTACTS
        elif ACTION in message \
                and message[ACTION] == GET_CONTACTS \
                and FROM in message \
                and self.user_list[message[FROM]] == client:
            response = RESPONSE_202
            print(f'processing contact list for {message["from"]}')
            c_list = self.database.db_contacts_list(message[FROM])
            print(f'contact list : {c_list}')
            response['contact_list'] = c_list
            if "user_list" in response:
                del response["user_list"]
            send_message(client, response)

        #  ACTION ADD_CONTACT
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
            response['user_list'] = [
                user.name for user in self.database.db_all_users_list()]
            if "contact_list" in response:
                del response["contact_list"]
            send_message(client, response)

            # Else send  Bad request

        # Если это запрос публичного ключа пользователя
        elif ACTION in message \
                and message[ACTION] == PUBLIC_KEY_REQUEST \
                and FROM in message:
            response = RESPONSE_511
            # if "data" in response:
            #     del response['data']
            response['pub_key'] = self.database.db_get_pubkey(
                message['target'])
            # может быть, что ключа ещё нет (пользователь никогда не логинился,
            # тогда шлём 400)
            if response['pub_key']:
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа для данного пользователя'
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)

        # Иначе отдаём Bad request

        else:
            response = {}
            response = RESPONSE_400
            response[ERROR] = 'Incorrect Query'
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def authorize_user(self, message, client):
        '''Метод реализующий авторизцию пользователей.'''
        # Если имя пользователя уже занято то возвращаем 400
        LOGGER.debug(f'Start auth process for {message[FROM]}')
        if message[FROM] in self.user_list.keys():
            response = RESPONSE_400
            response[ERROR] = 'Username already logged in '
            try:
                LOGGER.debug(f'Username busy, sending {response}')
                send_message(client, response)
            except OSError:
                LOGGER.debug('OS Error')
                pass
            self.clients.remove(client)
            client.close()
        # Проверяем что пользователь зарегистрирован на сервере.
        elif not self.database.db_check_user(message[FROM]):
            response = RESPONSE_400
            response[ERROR] = 'User has not been registered.'
            try:
                LOGGER.debug(f'Unknown username, sending {response}')
                send_message(client, response)
            except OSError:
                pass
            self.clients.remove(client)
            client.close()
        else:
            LOGGER.debug('Correct username, starting passwd check.')
            # Иначе отвечаем 511 и проводим процедуру авторизации
            # Словарь - заготовка
            message_auth = RESPONSE_511
            # Набор байтов в hex представлении
            random_str = binascii.hexlify(os.urandom(64))
            # В словарь байты нельзя, декодируем (json.dumps -> TypeError)
            message_auth[DATA] = random_str.decode('ascii')
            # Создаём хэш пароля и связки с рандомной строкой, сохраняем
            # серверную версию ключа
            hash = hmac.new(
                self.database.db_get_hash(
                    message[FROM]), random_str, 'MD5')
            digest = hash.digest()
            LOGGER.debug(f'Auth message = {message_auth}')
            try:
                # Обмен с клиентом
                send_message(client, message_auth)
                ans = get_message(client)
            except OSError as err:
                LOGGER.debug('Error in auth, data:', exc_info=err)
                client.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            # Если ответ клиента корректный, то сохраняем его в список
            # пользователей.
            if RESPONSE in ans and ans[RESPONSE] == 511 \
                    and hmac.compare_digest(digest, client_digest):
                self.user_list[message[FROM]] = client
                client_ip, client_port = client.getpeername()
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(message[FROM])
                # добавляем пользователя в список активных и если у него изменился открытый ключ
                # сохраняем новый
                self.database.db_user_login(
                    message[FROM], client_ip, client_port,
                    message['public_key'])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль.'
                try:
                    send_message(client, response)
                except OSError:
                    pass
                self.clients.remove(client)
                client.close()

    def service_update_lists(self):
        '''Метод реализующий отправки сервисного сообщения 205 клиентам.'''
        for client in self.user_list:
            try:
                send_message(self.user_list[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.user_list[client])

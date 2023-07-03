import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../')
from common.errors import ServerError
from client.client_variables import *
from client.client_database import *
from common.errors import IncorrectDataRecivedError, JSONDecodeError, NonDictInputError, ReqFieldMissingError, ServerError
from deco_log import log

# Логер и объект блокировки для работы с сокетом.
LOGGER = logging.getLogger('client_logger')
socket_lock = threading.Lock()


# Класс - Траннспорт, отвечает за взаимодействие с сервером
class ClientTransport(threading.Thread, QObject):
    # Сигналы новое сообщение и потеря соединения
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, ip_address, port, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        # Класс База данных - работа с базой
        self.database = database
        # Имя пользователя
        self.username = username
        # Сокет для работы с сервером
        self.transport = None
        # Устанавливаем соединение:
        self.connection_init(port, ip_address)
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.sdb_user_list_request()
            self.sdb_contacts_list_request()
        except OSError as err:
            if err.errno:
                LOGGER.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            LOGGER.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            LOGGER.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
            # Флаг продолжения работы транспорта.
        self.running = True

    # Функция инициализации соединения с сервером
    def connection_init(self, port, ip):
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(20)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если удалось
        connected = False
        for i in range(5):
            LOGGER.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # Если соединится не удалось - исключение
        if not connected:
            LOGGER.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        LOGGER.debug('Установлено соединение с сервером')

        # Посылаем серверу приветственное сообщение и получаем ответ что всё нормально или ловим исключение.
        try:
            with socket_lock:
                self.send_message(self.create_message_presence())
                response = self.get_message()
                self.process_server_response(response)
        except (OSError, json.JSONDecodeError):
            LOGGER.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        # Раз всё хорошо, сообщение о установке соединения.
        LOGGER.info('Соединение с сервером успешно установлено.')

    @log
    def get_message(self):
        """
        Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
        если приняточто-то другое отдаёт ошибку значения
        :param client:
        :return:
        """
        encoded_response = self.transport.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_response, bytes):
            try:
                json_response = encoded_response.decode(ENCODING)
                print(f'got message {json_response}')
                response = json.loads(json_response)
            except JSONDecodeError:
                raise IncorrectDataRecivedError
            if isinstance(response, dict):
                return response
            raise IncorrectDataRecivedError
        raise IncorrectDataRecivedError(' got not bytes input')

    @log
    def send_message(self, message):
        """
        Утилита кодирования и отправки сообщения
        принимает словарь и отправляет его
        :param sock:
        :param message:
        :return:
        """
        if not isinstance(message, dict):
            raise NonDictInputError
        # print(f'sending message l127 {message}')
        js_message = json.dumps(message)
        encoded_message = js_message.encode(ENCODING)
        self.transport.send(encoded_message)
        print(f'sending message {message} ')

    @log
    def create_message_presence(self):
        """Функция генерирует запрос о присутствии клиента"""
        msg_dict = {
            ACTION: PRESENCE,
            TIME: time.time(),
            FROM: self.username
        }
        LOGGER.debug(f'"PRESENCE" message for user {self.username} created')
        return msg_dict

    @log
    def create_message_exit(self):
        """Функция создаёт словарь с сообщением о выходе"""
        LOGGER.debug(f'"EXIT" message for user {self.client_username} created')
        return {
            ACTION: EXIT,
            TIME: time.time(),
            FROM: self.client_username
        }

    # Функция обрабатывающяя сообщения от сервера. Ничего не возращает. Генерирует исключение при ошибке.
    def process_server_response(self, message):
        LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        print(f"Processing of server response: {message}")

        # Если это подтверждение чего-либо

        if ACTION in message \
                and message[ACTION] == RESPONSE:
            print(f'processing response, message: {message}')
            if message[RESPONSE] == 200:
                print(f'response : 200 Ok')
                return f'response : 200 Ok'
            if message[RESPONSE] == 202 and 'user_list' in message:
                print(f'response : 202 Ok')
                return {'user_list': message['user_list']}
            if message[RESPONSE] == 202 and 'contact_list' in message:
                print(f'response : 202 Ok')
                return {'contact_list': message['contact_list']}

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о новом сообщении
        elif ACTION in message and message[ACTION] == MESSAGE \
                and FROM in message \
                and TO in message \
                and MESSAGE_TEXT in message \
                and message[TO] == self.username:
            LOGGER.debug(f'Получено сообщение от пользователя {message[FROM]}:{message[MESSAGE_TEXT]}')
            self.database.db_message_register(message[FROM], message[TO], message[MESSAGE_TEXT])
            self.new_message.emit(message[FROM])

        elif RESPONSE in message \
                and message[RESPONSE] == 400:
            print(f' ServerError : response 400 : {message[ERROR]}')
            return f' ServerError : response 400 : {message[ERROR]}'

        else:
            raise ReqFieldMissingError(RESPONSE)


    # Функция обновляющая контакт - лист с сервера
    def sdb_contacts_list_request(self):
        LOGGER.debug(f'Запрос контакт листа для пользователся {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            FROM: self.username
        }
        LOGGER.debug(f'Сформирован запрос {req}')
        with socket_lock:
            self.send_message(req)
            ans = self.get_message()
        LOGGER.debug(f'Got answer {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202\
                and 'contact_list' in ans:
            for contact in ans['contact_list']:
                self.database.db_add_contact(contact)
        else:
            print(f'Not able to refresh contacts lest')

    # Функция добавления пользователя в контакт лист
    def sdb_add_contact(self, contact):
        LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            FROM: self.username,
            CONTACT: contact
        }
        self.send_message(req)
        ans = self.get_message()
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise ServerError('Error at contact ctreation')
        print('Contact created')

    # Функция удаления пользователя из контакт листа
    def sdb_del_contact(self, contact):
        LOGGER.debug(f'sdb_remove_contact  {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            FROM: self.username,
            CONTACT: contact
        }
        self.send_message(req)
        ans = self.get_message()
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise ServerError('Ошибка удаления клиента')
        print('Удачное удаление')

    # Функция запроса таблицы известных пользователей.
    def sdb_user_list_request(self):
        LOGGER.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: 'get_users',
            TIME: time.time(),
            FROM: self.username
        }
        with socket_lock:
            self.send_message(req)
            ans = self.get_message()
            print(f'got answer : {ans}')
        if RESPONSE in ans \
                and ans[RESPONSE] == 202\
                and 'user_list' in ans:
            self.database.db_del_known_users()
            for contact in ans['user_list']:
                self.database.db_add_known_users(contact)
            return ans['user_list']
        else:
            LOGGER.error('"sdb_user_list_request" :Not able to receive user list')

    def sdb_user_check_request(self, his_username):
        LOGGER.debug(f'sdb_user_check_request {his_username}')
        req = {
            ACTION: 'check_user',
            TIME: time.time(),
            FROM: self.username,
            'check': his_username
        }
        self.send_message(req)
        ans = self.get_message()
        print(f'got answer : {ans}')
        if RESPONSE in ans \
                and ans[RESPONSE] == 202 \
                and 'user_checked' in ans:
            return ans['check_result']
        else:
            raise ServerError


    # Функция сообщающая на сервер о добавлении нового контакта
    def sdb_add_contact(self, contact):
        LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            FROM: self.username,
            CONTACT: contact
        }
        with socket_lock:
            self.send_message(req)
            self.process_server_response(self.get_message())

    # Функция удаления клиента на сервере
    def sdb_remove_contact(self, contact):
        LOGGER.debug(f'Удаление контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            FROM: self.username,
            CONTACT: contact
        }
        with socket_lock:
            self.send_message(req)
            self.process_server_ans(self.get_message())

    # Функция закрытия соединения, отправляет сообщение о выходе.
    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            FROM: self.username
        }
        with socket_lock:
            try:
                self.send_message(message)
            except OSError:
                pass
        LOGGER.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    # Функция отправки сообщения на сервер
    def sdb_send_text_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            FROM: self.username,
            TO: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            self.send_message(message_dict)
            print(f'sdb_send_text_msg : msg sent {message_dict}')
            self.process_server_response(self.get_message())
            print(f'sdb_send_text_msg : processing server response')
        LOGGER.info(f'Отправлено сообщение для пользователя {to}')
        # self.database.db_message_register(message_dict[FROM], message_dict[TO], message_dict[MESSAGE_TEXT])

    def run(self):
        LOGGER.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = self.get_message()
                except OSError as err:
                    if err.errno:
                        LOGGER.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    LOGGER.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_response(message)
                finally:
                    self.transport.settimeout(5)
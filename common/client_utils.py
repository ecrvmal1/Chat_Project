import argparse
import json
import logging
import sys
import time


from common.client_variables import *

from common.errors import IncorrectDataRecivedError, JSONDecodeError, NonDictInputError, ReqFieldMissingError, ServerError


from deco_log import log

LOGGER = logging.getLogger('client_logger')


@log
def create_message_presence(username):
    """Функция генерирует запрос о присутствии клиента"""
    msg_dict = {
        ACTION: PRESENCE,
        TIME: time.time(),
        FROM: username
    }
    LOGGER.debug(f'"PRESENCE" message for user {username} created')
    return msg_dict


@log
def process_server_response(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    """
    LOGGER.debug(f'Processing of server response: {message}')
    print(f"Processing of server response: {message}")
    if ACTION in message\
            and message[ACTION] == RESPONSE:
        print(f'processing response, message: {message}')
        if message[RESPONSE] == 200:
            print(f'response : 200 Ok')
            return
        if message[RESPONSE] == 202 and 'user_list' in message:
            print(f'response : 202 Ok')
            return {'user_list': message['user_list']}
        if message[RESPONSE] == 202 and 'contact_list' in message:
            print(f'response : 202 Ok')
            return {'contact_list': message['contact_list']}
        elif message[RESPONSE] == 400:
            print(f' ServerError : response 400 : {message[ERROR]}')
            return
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=DEFAULT_CLIENT_IP_ADDRESS, nargs='?')
    parser.add_argument('-p','--port', default=DEFAULT_CLIENT_PORT, type=int, nargs='?')
    # parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-u', '--user', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    # client_mode = namespace.mode
    client_username = namespace.user

    # проверим подходящий номер порта
    # if not 1023 < server_port < 65536:
    #     print(
    #         f'Incorrect port number: {server_port}. '
    #         f'Port numbers must be in range 1024 ... 65535. Client program closed.')
    #     LOGGER.critical(
    #         f'Incorrect port number: {server_port}. '
    #         f'Port numbers must be in range 1024 ... 65535. Client program closed.')
    #     sys.exit(1)

    # # Проверим допустим ли выбранный режим работы клиента
    # if client_mode not in ('listen', 'send'):
    #     LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
    #                     f'допустимые режимы: listen , send')
    #     sys.exit(1)

    return server_address, server_port, client_username


@log
def get_message(client):
    """
    Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
    если приняточто-то другое отдаёт ошибку значения
    :param client:
    :return:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
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
    raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    """
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    print(f'sending message {message}')
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
    print(f'sending message {message} t0 {sock}')


# Функция запрос контакт листа
def sdb_contacts_list_request(sock, name):
    LOGGER.debug(f'Запрос контакт листа для пользователся {name}')
    req = {
        ACTION: 'get_contacts',
        TIME: time.time(),
        FROM: name
    }
    LOGGER.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    print(f'got answer : {ans}')
    LOGGER.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans['contact_list']
    else:
        raise ServerError


# Функция добавления пользователя в контакт лист
def sdb_add_contact(sock, username, contact):
    LOGGER.debug(f'Создание контакта {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        FROM: username,
        CONTACT: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Error at contact ctreation')
    print('Contact created')


# Функция запроса списка известных пользователей
def sdb_user_list_request(sock, username):
    LOGGER.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: 'get_users',
        TIME: time.time(),
        FROM: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    print(f'got answer : {ans}')
    if RESPONSE in ans \
            and ans[RESPONSE] == 202 \
            and 'user_list' in ans :
        return ans['user_list']
    else:
        raise ServerError


# Функция удаления пользователя из контакт листа
def sdb_remove_contact(sock, username, contact):
    LOGGER.debug(f'Deleting contact  {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        FROM: username,
        CONTACT: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка удаления клиента')
    print('Удачное удаление')


# Функция инициализатор базы данных. Запускается при запуске, загружает данные в базу с сервера.
def sdb_database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = sdb_user_list_request(sock, username)
    except ServerError:
        LOGGER.error('Ошибка запроса списка известных пользователей.')
    else:
        for user in users_list:
            database.db_add_known_users(user)

    # Загружаем список контактов
    try:
        contacts_list = sdb_contacts_list_request(sock, username)
    except ServerError:
        LOGGER.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.db_add_contact(contact)



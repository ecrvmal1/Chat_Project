import argparse
import json
import logging
import sys
import time

sys.path.append('../')

from Lesson3.common.client_variables import ACTION, MESSAGE, MESSAGE_TEXT, SENDER, TIME, PRESENCE, FROM, TO, \
    DEFAULT_CLIENT_IP_ADDRESS, DEFAULT_CLIENT_PORT, ENCODING, MAX_PACKAGE_LENGTH, RESPONSE, ERROR, EXIT

from Lesson3.common.errors import IncorrectDataRecivedError, JSONDecodeError, NonDictInputError, ReqFieldMissingError, ServerError


from Lesson3.deco_log import log

LOGGER = logging.getLogger('client_logger')


@log
def create_message_presence(username):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        FROM: username
    }
    LOGGER.debug(f'"PRESENCE" message for user {username} created')
    return out


@log
def process_server_response(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    """
    LOGGER.debug(f'Processing of server response: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
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
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
    print(f'sending message {message} t0 {sock}')





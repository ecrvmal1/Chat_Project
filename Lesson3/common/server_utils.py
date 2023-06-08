import argparse
import json
import logging
import sys

from Lesson3.common.errors import NonDictInputError, IncorrectDataRecivedError, JSONDecodeError

sys.path.append('../')

from common.server_variables import ACTION, PRESENCE, TIME, ACCOUNT_NAME, USER, MAX_PACKAGE_LENGTH, \
RESPONSE, MESSAGE, MESSAGE_TEXT, ERROR, DEFAULT_SERVER_IP_ADDRESS, DEFAULT_SERVER_PORT, ENCODING
from deco_log import log

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server_logger')


@log
def process_client_message(message, messages_list, client):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    print(f'processing message {message} from {client}')
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        print (f'message added to message_list {messages_list}')
        return
    # Иначе отдаём Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        print(f'sent error message to {client}')
        return


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_SERVER_IP_ADDRESS, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


@log
def send_message(sock, message):
    """
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    """
    print(f'sending message {message}  to {sock}')
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)



@log
def get_message(client):
    """
    Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
    если приняточто-то другое отдаёт ошибку значения
    :param client:
    :return:
    """
    try:
        encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    except ConnectionResetError:
        raise ConnectionResetError
    if isinstance(encoded_response, bytes):
        try:
            json_response = encoded_response.decode(ENCODING)
            response = json.loads(json_response)
        except JSONDecodeError:
            raise IncorrectDataRecivedError
        if isinstance(response, dict):
            print(f'got message {response} from {client}')
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError






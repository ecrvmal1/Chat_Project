import argparse
import json
import logging
import sys

from common.errors import NonDictInputError, IncorrectDataRecivedError, JSONDecodeError


from common.server_variables import *
from deco_log import log

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server_logger')


@log
def get_message(client):
    """
    Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
    если приняточто-то другое отдаёт ошибку значения
    :param client:
    :return:
    """
    message_encoded = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(message_encoded, bytes):
        try:
            print(f'          trying decode {message_encoded}')
            message_decoded = message_encoded.decode(ENCODING)
            print(f'          trying make dict from {message_decoded}')
            message_dict = json.loads(message_decoded)
            print(f'          dict composed {message_dict}')
        except json.JSONDecodeError:
            print(f' got message {message_encoded}, fail to decode the message')
            return
        if isinstance(message_dict, dict):
            print(f'got message {message_dict} from {client}')
            return message_dict
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_SERVER_IP_ADDRESS, nargs='?')
    parser.add_argument('-u', default=DEFAULT_USERNAME, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    # listen_username = namespace.u

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Incorrect PORT nmber '
            f'{listen_port}. Try port in range :  1024 ... 65535.')
        sys.exit(1)

    return listen_address, listen_port\
        # , listen_username


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













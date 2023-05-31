import sys
import re
import os
import time
import json
import logging
from socket import *

from common.server_variables import ENCODING, RESPONSE, ERROR, MAX_PACKAGE_LENGTH, USER, \
    ACTION, PRESENCE, TIME, ACCOUNT_NAME

LOGGER = logging.getLogger('server_logger')

def get_ip_address(args_list) -> str:
    ip_addr = None
    if '-a' in args_list:
        try:
            ip_addr = str(args_list[args_list.index('-a') + 1])
        except IndexError:
            print('after "-a", Server IP address must be indicated')
            sys.exit(1)
        reg_exp = re.compile(r'([0-9]{1,3}[\.]){3}[0-9]{1,3}')
        if reg_exp.match(ip_addr):
            pass
        else:
            print(' IP address value must be in format "xxx.xxx.xxx.xxx" ')
            sys.exit(1)
    return ip_addr


def get_port(args_list) -> int:
    port_number = None
    if '-p' in args_list:
        try:
            port_number = int(sys.argv[sys.argv.index('-p') + 1])
        except IndexError:
            print('after "-p", server port value must be indicated')
            sys.exit(1)
        if port_number < 1024 or port_number > 65535:
            print(' Server port number must be in interval 1024...65535')
            exit(1)
    return port_number


def process_incoming_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    """
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and 'user' in message \
            and message['user']['account_name'] == 'Guest':
        # print('RESPONSE: 200')
        LOGGER.info('RESPONSE: 200')
        return {'response': {RESPONSE: 200}}
    if ACTION in message \
            and message[ACTION] == 'msg' \
            and TIME in message \
            and 'to' in message \
            and message['from'] == 'Guest':
        # print('RESPONSE: 201')
        LOGGER.info('RESPONSE: 201')
        return {'response': {RESPONSE: 201}}
    if ACTION in message \
            and message[ACTION] == 'quit':
        # print('quit , RESPONSE: 202')
        LOGGER.info('RESPONSE: 202')
        return {'response': {RESPONSE: 202},
                'quit': " "}
    print('RESPONSE: 400, error: Bad Request')
    LOGGER.error('RESPONSE: 400, error: Bad Request')
    return {'response': {
        'response': 400,
        'error': 'Bad Request'
    }}


def send_message(sock, message):
    json_msg = json.dumps(message)
    encoded_msg = json_msg.encode(ENCODING)
    # print(f'sending message:  {encoded_msg}')
    sock.send(encoded_msg)
    LOGGER.info('message has been sent')


def get_message(client) -> dict:
    """
    Утилита приёма и декодирования сообщения
    The function receives and decodes messages from Server
    if received unexpected responce, the function raise error
    :param client: bytes
    :return: dict
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    # print(f'encoded response : {encoded_response}')
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            LOGGER.info('got message from client')
            return response
    LOGGER.error('got message from client with incorrect encoding')
    raise ValueError









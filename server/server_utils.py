import argparse
import configparser
import json
import logging
import os
import sys
import subprocess
import socket

sys.path.append('../')
import log.server_log_config
from common.errors import NonDictInputError, IncorrectDataRecivedError, JSONDecodeError
from server.server_variables import *
from server.server_decos import log

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
            # print(f'          trying decode {message_encoded}')
            message_decoded = message_encoded.decode(ENCODING)
            # print(f'          trying make dict from {message_decoded}')
            message_dict = json.loads(message_decoded)
            # print(f'          dict composed {message_dict}')
        except JSONDecodeError:
            # print(f' got message {message_encoded}, fail to decode the message')
            raise JSONDecodeError
            # return
        if isinstance(message_dict, dict):
            print(f'got message {message_dict} ')
            return message_dict
        else:
            raise IncorrectDataRecivedError('msg is not dict')
    else:
        raise IncorrectDataRecivedError('incoming msg is not bytes')


@log
def arg_parser(default_ip=None, default_port=None):
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_SERVER_IP_ADDRESS, nargs='?')
    parser.add_argument('-u', default=DEFAULT_USERNAME, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    if default_ip:
        listen_address = default_ip
    listen_port = int(namespace.p)
    if default_port:
        listen_port = int(default_port)
    # listen_username = namespace.u

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Incorrect PORT nmber '
            f'{listen_port}. Try port in range :  1024 ... 65535.')
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


def pid_used_port(port_numb):
    params = str()
    cmd = ['netstat', '-ntlp']
    param = []
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        line = subproc.stdout.readline()
        decoded_line = line.decode('ASCII')
        if str(port_numb) in decoded_line:
            params = decoded_line.split()
            param = params[6].split('/')
            # print(f' decoded_line: {decoded_line}')
            # print(f' param[0] : {param[0]}')
        if not line:
            break
        subproc.terminate()
        print(f'port {port_numb}  is in use, process : {params}')
    try:
        return param[0]
    except IndexError:
        return


@log
def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    config_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(config_path, 'server.ini')
    config.read(config_file)
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по
    # умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str('Default_port'))
        config.set('SETTINGS', 'Listen_ip', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server.db3')
        return config


def print_cli_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


if __name__ == '__main__':
    print(f'pid = {pid_used_port(7777)}')














import json
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
    """
    the function indicates number of port which occupies port 7777
    :param port_numb:
    :return:
    """
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


def print_cli_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


if __name__ == '__main__':
    print(f'pid = {pid_used_port(7777)}')













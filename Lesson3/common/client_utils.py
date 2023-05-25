import sys
import re
import os
import time
import json
import socket

from common.client_variables import ENCODING, RESPONSE, ERROR, MAX_PACKAGE_LENGTH, USER


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


def menu_action():
    while True:
        print('Main menu:  1 - connect to server \n'
              '            2 - message  \n'
              '            3 - quit \n'
              '            4 - join to chat \n'
              '            5 - leave chat \n')
        action = int(input("enter code of action: "))
        if action in range(1, 5):
            break
    return action


def client_connection(ipaddress, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ipaddress, port))
    except Exception:
        print('Server not responding')
        sys.exit(1)
    return True, s


def terminal_info(status, message):
    # print(f"terminal : status : {status}, message {message} ")
    # os.system('clear')
    # print(f"terminal : status : {status}, message {message} ")
    conn = "Connected" if status is True else "Disconnected"
    print('==================================')
    print( f' status {conn}')
    print('==================================')
    print(f'Message : {message}')
    print('==================================')
    action = menu_action()
    return action


def presence_msg(account_name='Guest'):
    """
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    """
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    out = {
        'action': 'presence',
        'time': time.time(),
        'type': 'status',
        'user': {
            "account_name": account_name,
            "status": "connected"
        }
    }
    return out


def get_message(client) -> dict:
    """
    Утилита приёма и декодирования сообщения
    The function receives and decodes messages from Server
    if received unexpected responce, the function raise error
    :param client: bytes
    :return: dict
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
    raise ValueError


def send_message(sock, message):
    json_msg = json.dumps(message)
    encoded_msg = json_msg.encode(ENCODING)
    # print(f'encoded msg = {encoded_msg}')
    sock.send(encoded_msg)
    # print('message sent to server')


def process_ans(message):

    """
    The function check server response
    :param message:
    :return: string :  '200 : OK'  or  '400 : {message[ERROR]}
    """
    # print(f'process incoming message {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f'200 : OK'
        elif message[RESPONSE] == 201:
            return f'201 : OK'
        elif message[RESPONSE] == 400:
            return f'400 : Error '
        else:
            raise ValueError


def client_disconnection(sock):
    sock.close()
    return False

def user_msg() -> dict:
    """
    Функция генерирует cooбщение клиента
    :param account_name:
    :return: dict
    """
    # {
    # "action": "msg",
    # "time": <unix timestamp>,
    # "to": "account_name",
    # "from": "account_name",
    # "encoding": "ascii",
    # "message": "message"
    # }
    while True:
        user_message = str(input("Please enter message (500 char max) : "))
        if len(user_message) < 500:
            break
    while True:
        user_to = str(input("Please enter receiver User_ID :  "))
        if len(user_message) < 25:
            break
    out = {
        'action': "msg",
        'time': time.time(),
        'to': user_to,
        'from': 'Guest',
        'encoding': ENCODING,
        'message': user_message
        }
    return out





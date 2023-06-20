import socket
import sys
import json
import logging
import threading
import time

# sys.path.append('../')

import log.client_log_config
from common.errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError, JSONDecodeError
from deco_log import log

from common.client_variables import *
from Lesson3.common.client_utils import send_message, get_message, create_message_presence, arg_parser, \
    process_server_response
from metaclasses import ClientMaker

LOGGER = logging.getLogger('client_logger')


def print_help():
    """Функция выводящяя справку по использованию"""
    print(' Please enter command:')
    print('  s - send message.')
    print('  h - print help')
    print('  e - disconnect and exit')



class MessageReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, client_username, sock):
        self.client_username = client_username
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                print(f'message = {message}')
                if ACTION in message \
                        and message[ACTION] == MESSAGE \
                        and FROM in message \
                        and TO in message \
                        and MESSAGE_TEXT in message \
                        and message[TO] == self.client_username:
                    print(f'\n Got message from user : {message[FROM]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'Got message from user : {message[FROM]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(f'Got incorrect message from server: {message}')
            except IncorrectDataRecivedError:
                LOGGER.error(f'Not able to decode received message.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, JSONDecodeError):
                LOGGER.critical(f'Connection to server lost.')
                break



class MessageSender(threading.Thread):
# class MessageSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, client_username, sock):
        self.client_username = client_username
        self.sock = sock
        super().__init__()

    @log
    def create_message_exit(self):
        """Функция создаёт словарь с сообщением о выходе"""
        LOGGER.debug(f'"EXIT" message for user {self.client_username} created')
        return {
            ACTION: EXIT,
            TIME: time.time(),
            FROM: self.client_username
        }

    @log
    def create_message(self):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :param sock:
        :param username:
        :return:
        """
        LOGGER.debug(f'"CREATE_MESSAGE Function " called ')
        to_user = input("Enter receiver's Username : ")
        message = input('Enter message to send     : ')
        message_dict = {
            ACTION: MESSAGE,
            FROM: self.client_username,
            TO: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Created dict to be send: {message_dict}')
        try:
            LOGGER.debug(f'Create_message Trying to send message {message_dict}')
            send_message(self.sock, message_dict)
            LOGGER.info(f'Message to user  {to_user} sent')
        except:
            LOGGER.critical('Connection to server lost ')
            sys.exit(1)


    @log
    # def sender_main_cycle(self):
    def run(self):
        while True:
            # LOGGER.debug('SENDER_main_cycle')
            print_help()
            command = input('Enter command letter: ')
            if command == 's':
                self.create_message()
            elif command == 'h':
                print_help()
            elif command == 'e':
                try:
                    send_message(self.sock, self.create_message_exit())
                except:
                    pass
                print('Close connection')
                LOGGER.info('Close Client program by operator')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(1.0)
                break
            else:
                print('the command is not correct, try again \n'
                      'h - print help message.')


@log
def main():
    print('********** CHAT CLIENT RUNNING *************' )
    """Загружаем параметы коммандной строки"""
    server_address, server_port, client_username = arg_parser()
    if not client_username:
        client_username = input('Please enter your username: ')

    LOGGER.info(
        f'Client runs , Server IP address : {server_address}, '
        f'Port number : {server_port}, Usernabe: {client_username}')
    print(
        f'Client runs , Server IP address : {server_address}, '
        f'Port number : {server_port}, Usernabe: {client_username}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_message_presence(client_username))
        answer = process_server_response(get_message(transport))
        LOGGER.info(f'Connection to server established,  Server response: {answer}')
        print(f'Connection to server established,  Server response: {answer}')
    except json.JSONDecodeError:
        LOGGER.error('Not able to decode JSON string.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'Server returns ERROR at connection attempt: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'Missing fields in server response {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Server not available {server_address}:{server_port}, '
            f'Server refused correction request')
        sys.exit(1)

    else:
        # receiver = threading.Thread(target=display_incoming_message, args=(transport, client_username))
        msg_reader = MessageReader(client_username, transport)
        msg_reader.daemon = True
        msg_reader.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        msg_sender = MessageSender(client_username , transport)
        # user_interface = threading.Thread(target=main_menu, args=(transport, client_username))
        msg_sender.daemon = True
        msg_sender.start()
        LOGGER.debug('Threads run')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if msg_reader.is_alive() and msg_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()





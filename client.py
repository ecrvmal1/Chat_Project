import socket
import sys
import json
import threading
import time

# sys.path.append('../')

from common.errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError, JSONDecodeError
from deco_log import log

from common.client_variables import *
from common.client_utils import *
from metaclasses import ClientMaker
from client_database import ClientDatabase

LOGGER = logging.getLogger('client_logger')
sock_lock = threading.Lock()
database_lock = threading.Lock()


def print_help():
    """Функция выводящяя справку по использованию"""
    print(' Please enter command:')
    print('  help :         get help')
    print('  message :      send message.')
    print('  history :      print message history')
    print('  contacts :     print contact list')
    print('  edit :         edit contact list')
    print('  exit :         disconnect and exit')


class MessageReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, client_username, sock, database):
        self.client_username = client_username
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1.0)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                    # print(f'message = {message}')
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
                    if ACTION in message \
                            and message[ACTION] == RESPONSE:
                        print(f'processing response, message: {message}')
                        if message[RESPONSE] == 200:
                            print(f'response : 200 Ok')
                            return
                        if message[RESPONSE] == 202 and 'user_list' in message:
                            print(f'response : 202 Ok adding user_list')
                            for usr in message['user_list']:
                                self.database.db_add_known_users(usr)
                        if message[RESPONSE] == 202 and 'contact_list' in message:
                            for cont in message['contact_list']:
                                self.database.db_add_contact(cont)
                        elif message[RESPONSE] == 400:
                            print(f' ServerError : response 400 : {message[ERROR]}')
                            return
                    else:
                        LOGGER.error(f'Got incorrect message from server: {message}')
                except IncorrectDataRecivedError:
                    LOGGER.error(f'Not able to decode received message.')
                except (OSError, ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError):
                    LOGGER.critical(f'Connection to server lost.')
                    break

                # if response got correctly, print to console and write to DB
                else:
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
                        with database_lock:
                            try:
                                self.database.db_message_register(message)
                            except:
                                logger.error('Interaction with DB fault')
                    else:
                        LOGGER.error(f'Got incorrect message from server: {message}')



class MessageSender(threading.Thread):
# class MessageSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, client_username, sock, database):
        self.client_username = client_username
        self.sock = sock
        self.database = database
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

        # check if receiver exists
        with database_lock:
            if not self.database.db_check_known_user(to_user):
                LOGGER.error(f'Попытка отправить сообщение незарегистрированому получателю: {to_user}')
                return

        message_dict = {
            ACTION: MESSAGE,
            FROM: self.client_username,
            TO: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Created dict to be send: {message_dict}')
        with database_lock:
            self.database.db_message_register(message_dict)
        with sock_lock:
            try:
                LOGGER.debug(f'Create_message Trying to send message {message_dict}')
                send_message(self.sock, message_dict)
                LOGGER.info(f'Message to user  {to_user} sent')
            except OSError as err:
                if err.errno:
                    LOGGER.critical('Connection to server lost, exiting.')
                    time.sleep(0.5)
                    sys.exit(1)
                else:
                    LOGGER.error('Error at message sending')


    @log
    # def sender_main_cycle(self):
    def run(self):
        while True:
            # LOGGER.debug('SENDER_main_cycle')
            print_help()
            command = input('Enter command letter: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                print_help()
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_message_exit())
                    except OSError as err:
                        pass
                    print('Close connection')
                    LOGGER.info('Close Client program by operator')
                    # the timeout need for sending exit message
                    time.sleep(0.8)
                    break

            # Список контактов
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.db_get_contacts()
                for contact in contacts_list:
                    print(contact)

            # Редактирование контактов
            elif command == 'edit':
                self.edit_contacts()

            # история сообщений.
            elif command == 'history':
                self.print_history()

            else:
                print('the command is not correct, try again \n'
                      'h - print help message.')

    # function for getting list of messages
    def print_history(self):
        print('Enter what you want :'
              'in       for incoming messages'
              'out      for outgoing messages'
              'Enter      for all messages')

        ask = input()
        with database_lock:
            if ask == 'in':
                history_list = self.database.db_get_message_history(to_who=self.client_username)
                for message in history_list:
                    print(f'\n  from: "{message[0]}" to : "{message[1]}" :\n'
                          f'at : {message[3]}   text : {message[2]} ')
            elif ask == 'out':
                history_list = self.database.db_get_message_history(from_who=self.client_username)
                for message in history_list:
                    print(f'\n  from: "{message[0]}" to : "{message[1]}" :\n'
                          f'at : {message[3]}   text : {message[2]} ')
            else:
                history_list = self.database.db_get_message_history()
                for message in history_list:
                    print(f'\n  from: "{message[0]}" to : "{message[1]}" :\n'
                          f'at : {message[3]}   text : {message[2]} ')

        # Функция изменеия контактов

    def sdb_edit_contacts(self):
        print('Enter what you want :'
              'del  :   to delete contact' 
              'add  :   to add contact')
        ans = input()
        if ans == 'del':
            contact_to_del = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.db_check_contact(contact_to_del):
                    self.database.db_del_contact(contact_to_del)
                else:
                    LOGGER.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            contact_name = str(input('Введите имя создаваемого контакта: '))
            if self.database.check_user(contact_name):
                with database_lock:
                    self.database.add_contact(contact_name)
                with sock_lock:
                    try:
                        sdb_add_contact(self.sock, self.client_username, contact_name)
                    except ServerError:
                        LOGGER.error('Не удалось отправить информацию на сервер.')


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
        transport.settimeout(5)
        transport.connect((server_address, server_port))
        send_message(transport, create_message_presence(client_username))
        message = get_message(transport)
        print(f'got message from server : {message}')
        answer = process_server_response(message)
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
        # DB initialization
        database = ClientDatabase(client_username)
        sdb_database_load(transport, database, client_username)

        # receiver = threading.Thread(target=display_incoming_message, args=(transport, client_username))
        msg_reader = MessageReader(client_username, transport, database)
        msg_reader.daemon = True
        msg_reader.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        msg_sender = MessageSender(client_username , transport, database)
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





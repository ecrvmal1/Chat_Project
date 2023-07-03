import socket
import sys
import threading
import logging
import argparse
from PyQt5.QtWidgets import QApplication

from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog
from client.transport import ClientTransport
from common.errors import ServerError
from metaclasses import ClientMaker
from client.client_database import ClientDatabase
from deco_log import log

from client.client_variables import *

LOGGER = logging.getLogger('client_logger')
sock_lock = threading.Lock()
database_lock = threading.Lock()

#
# def print_help():
#     """Функция выводящяя справку по использованию"""
#     print(' Please enter command:')
#     print('  help :         get help')
#     print('  message :      send message.')
#     print('  history :      print message history')
#     print('  contacts :     print contact list')
#     print('  edit :         edit contact list')
#     print('  exit :         disconnect and exit')

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
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f' Trying to start client on port: {server_port}. Exiting.')
        exit(1)

    return server_address, server_port, client_username


def main():
    server_address, server_port, username = arg_parser()

    client_app = QApplication(sys.argv)

    # remove in final
    # username = 'user1'
    # client_name = 'user1'
    if not username:
        start_dialog = UserNameDialog()
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, инааче выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
            print(f' client name = {client_name}')
        else:
            exit(0)
    LOGGER.info(f'client run with ip : {server_address}, '
                f'port: {server_port}, '
                f'username: {client_name}')

    database = ClientDatabase(client_name)
    try:
        transport = ClientTransport(server_address, server_port, database, client_name)
    except ServerError as err:
        print(f'Transport error : {err.text}')
        exit(1)
    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database,transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()





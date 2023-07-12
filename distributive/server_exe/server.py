"""  THE SERVER SCRIPT """
import argparse
import configparser
import socket
import select
import sys
import threading
import os
from json import JSONDecodeError

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

from server.server_core import ServerMessageProcessor

from server.server_utils import get_message, send_message, pid_used_port, print_cli_help
from server.s_main_window import MainWindow
from common.errors import IncorrectDataRecivedError
from common.descriptors import Port
from server.server_database import *
from server.server_variables import *
from server.server_decos import log

LOGGER = logging.getLogger('server_logger')

new_connection = False
# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
connflag_lock = threading.Lock()


@log
def arg_parser(default_ip=None, default_port=None):
    """Парсер аргументов коммандной строки"""
    # print(f' arg parser l34 {default_ip}, {default_port} ')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_SERVER_IP_ADDRESS, nargs='?')
    # parser.add_argument('-u', default=DEFAULT_USERNAME, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    if default_ip:
        listen_address = default_ip
    listen_port = int(namespace.p)
    if default_port:
        listen_port = int(default_port)
    gui_flag = namespace.no_gui
    # listen_username = namespace.u

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Incorrect PORT number : {listen_port} ')
        sys.exit(1)
    # print(f' argparcer l_54 {listen_address} {listen_port} {gui_flag}')
    return listen_address, listen_port, gui_flag



@log
def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    config_path = os.getcwd()
    config_file = os.path.join(config_path, 'server.ini')
    config.read(config_file)
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по
    # умолчанию.
    if "SETTINGS" in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str('Default_port'))
        config.set('SETTINGS', 'Listen_ip', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server.db3')
        return config



@log
def main():
    # ------------------  process  server.ini --------------

    config = config_load()
    listen_address, listen_port, gui_flag = arg_parser(
        config["SETTINGS"]["Listen_ip"],
        config["SETTINGS"]["Default_port"])

    database_path = os.path.join(config["SETTINGS"]["Database_path"],
                                 config["SETTINGS"]["Database_file"])
    database = ServerStorage(database_path)
    server = ServerMessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()


    # ----------------------- CLI -----------------------------
    if gui_flag:
        while True:
            print_cli_help()
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                # Если выход, то завршаем основной цикл сервера.
                server.running = False
                server.join()
                break

    # ------------------------- GUI ---------------------------
    # Create Graphics environment for server
    else:
        # Создаём графическое окуружение для сервера:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False

    # # Таймер, обновляющий список клиентов 1 раз в секунду
    # timer = QTimer()
    # timer.timeout.connect(gui_list_update)
    # timer.start(1000)
    #
    # # link buttons to procedures
    # main_window.refresh_button.triggered.connect(gui_list_update)
    # main_window.history_button.triggered.connect(gui_show_statistics)
    # main_window.config_button.triggered.connect(gui_server_config)
    #
    # # run GUI
    # server_app.exec_()




if __name__ == '__main__':
    main()

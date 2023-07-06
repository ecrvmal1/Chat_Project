"""  THE SERVER SCRIPT """
import configparser
import socket
import select
import sys
import threading
import os
from json import JSONDecodeError

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from server.server_core import Server_Message_Processor
from server.server_variables import *
from server.server_utils import arg_parser, get_message, send_message, pid_used_port, config_load, print_cli_help

from common.errors import IncorrectDataRecivedError
from common.descriptors import Port
from server.server_database import *

LOGGER = logging.getLogger('server_logger')

new_connection = False
# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
connflag_lock = threading.Lock()



def main():
    # ------------------  process  server.ini --------------

    config = config_load()

    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_ip'])

    database_path = os.path.join(config['SETTINGS']['Database_path'],
                                 config['SETTINGS']['Database_file'])
    database = ServerStorage(database_path)

    server = Server_Message_Processor(listen_address, listen_port, database)
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

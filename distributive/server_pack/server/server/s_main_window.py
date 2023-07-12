import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QTimer
from server.stat_window import StatWindow
from server.config_window import ConfigWindow
from server.add_user import RegisterUser
from server.remove_user import RemUserDialog


class MainWindow(QMainWindow):
    '''Класс - основное окно сервера.'''

    def __init__(self, database, server, config):
        # Конструктор предка
        super().__init__()

        # База данных сервера
        self.database = database

        self.server_thread = server
        self.config = config

        # Ярлык выхода
        self.exitAction = QAction('Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        # Кнопка обновить список клиентов
        self.refresh_button = QAction('Refresh List', self)

        # Кнопка настроек сервера
        self.config_btn = QAction('Server Settings', self)

        # Кнопка регистрации пользователя
        self.usr_register_btn = QAction('User registration', self)

        # Кнопка удаления пользователя
        self.usr_remove_btn = QAction('User removal', self)

        # Кнопка вывести историю сообщений
        self.show_history_button = QAction('Users History', self)

        # Статусбар
        self.statusBar()
        self.statusBar().showMessage('Server Working')

        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.usr_register_btn)
        self.toolbar.addAction(self.usr_remove_btn)

        # Настройки геометрии основного окна
        # Поскольку работать с динамическими размерами мы не умеем, и мало
        # времени на изучение, размер окна фиксирован.
        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel('Connected Clients:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        # Окно со списком подключённых клиентов.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        # Таймер, обновляющий список клиентов 1 раз в секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        # Связываем кнопки с процедурами
        self.refresh_button.triggered.connect(self.create_users_model)
        self.show_history_button.triggered.connect(self.show_statistics)
        self.config_btn.triggered.connect(self.server_config)
        self.usr_register_btn.triggered.connect(self.reg_user)
        self.usr_remove_btn.triggered.connect(self.remove_user)

        # Последним параметром отображаем окно.
        self.show()

    def create_users_model(self):
        '''Метод заполняющий таблицу зарегистрированных пользователей.'''
        list_users = self.database.db_active_users_list()
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Username', 'IP Address', 'Port', 'Last Login'])
        for row in list_users:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            # Уберём милисекунды из строки времени, т.к. такая точность не
            # требуется.
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            list.appendRow([user, ip, port, time])
        self.active_clients_table.setModel(list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()

    def server_config(self):
        '''Метод создающий окно с настройками сервера.'''
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        '''Метод создающий окно регистрации пользователя.'''
        global reg_window
        reg_window = RegisterUser(self.database, self.server_thread)
        reg_window.show()

    def remove_user(self):
        '''Метод создающий окно удаления пользователя.'''
        global rem_window
        rem_window = RemUserDialog(self.database, self.server_thread)
        rem_window.show()

    def show_statistics(self):
        '''Метод создающий окно со статистикой клиентов.'''
        global stat_window
        stat_window = StatWindow(self.database)
        stat_window.show()

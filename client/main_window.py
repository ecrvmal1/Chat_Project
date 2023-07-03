import datetime
import time

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
import sys
import json
import logging

# from client.main_window_conv import Ui_MainClientWindow
from client.client_gui1 import Ui_MainClientWindow

sys.path.append('../')

from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from client.client_database import ClientDatabase
from client.transport import ClientTransport
from client.start_dialog import UserNameDialog
from common.errors import ServerError

logger = logging.getLogger('client')


# Класс основного окна
class ClientMainWindow(QMainWindow):
    def __init__(self, database, transport):
        super().__init__()
        # основные переменные
        self.database = database
        self.transport = transport

        # Загружаем конфигурацию окна из дизайнера
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # Кнопка "Выход"
        self.ui.menu_exit.triggered.connect(qApp.exit)

        # Кнопка отправить сообщение
        self.ui.btn_send.clicked.connect(self.send_message)

        # "добавить контакт"
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        # Удалить контакт
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)
        self.ui.label_username.setText(f' User : {self.transport.username}')
        self.ui.label_connection.setText(f'Connection: Connected')

        # Даблклик по листу контактов отправляется в обработчик
        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    # Деактивировать поля ввода
    def set_disabled_input(self):
        # Надпись  - получатель.
        self.ui.label_new_message.setText('To choose message receiver, take doubleclick on his name ')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        # Поле ввода и кнопка отправки неактивны до выбора получателя.
        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    # Заполняем историю сообщений.
    def history_list_update(self):
        filtered_list =[]
        message_history = self.database.db_get_message_history()
        list = sorted(message_history, key=lambda item: item[2])
        for item in list:
            if item[0] == self.current_chat and item[1] == self.transport.username:
                filtered_list.append(item)
            elif item[1] == self.current_chat and item[0] == self.transport.username:
                filtered_list.append(item)
            else:
                pass
        # Если модель не создана, создадим.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        # Очистим от старых записей
        self.history_model.clear()
        # Берём не более 20 последних записей.
        length = len(filtered_list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_index, length):
            item = filtered_list[i]
            if item[1] == self.transport.username:
                mess = QStandardItem(f'Incoming from {item[0]} at {item[2].replace(microsecond=0)}:\n {item[3]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Outgoing to {item[1]} at {item[2].replace(microsecond=0)}:\n {item[3]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    # Функция обработчик даблклика по контакту
    def select_active_user(self):
        # Выбранный пользователем (даблклик) находится в выделеном элементе в QListView
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        # вызываем основную функцию
        self.set_active_user()

    # Функция устанавливающяя активного собеседника
    def set_active_user(self):
        # Ставим надпись и активируем кнопки
        self.ui.label_new_message.setText(f'Enter Message for : {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
        self.history_list_update()

    # Функция обновляющяя контакт лист
    def clients_list_update(self):
        contacts_list = self.database.db_get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    # Функция добавления контакта
    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    # Функция - обработчик добавления, сообщает серверу, обновляет таблицу и список контактов
    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    # Функция добавляющяя контакт в базы
    def add_contact(self, new_contact):
        try:
            self.transport.sdb_add_contact(new_contact)
            self.ui.label_server_info.setText(f'Server Info: Contact Added')
        except ServerError as err:
            self.messages.critical(self, 'Server Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Server Connection Lost')
                self.close()
            self.messages.critical(self, 'Error', 'Timeout expired!')
        else:
            self.database.db_add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Contact added {new_contact}')
            self.messages.information(self, 'Success', 'Contact Added.')

    # Функция удаления контакта
    def delete_contact_window(self):
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    # Функция обработчик удаления контакта, сообщает на сервер, обновляет таблицу контактов
    def delete_contact(self, item):
        selected = item.selector.currentText()
        try:
            self.transport.sdb_del_contact(selected)
            self.ui.label_server_info.setText(f'Server Info: Contact Deleted')
        except ServerError as err:
            self.messages.critical(self, 'Server Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection to server lost!')
                self.close()
            self.messages.critical(self, 'Error', 'Timeout Expired!')
        else:
            self.database.db_del_contact(selected)
            self.clients_list_update()
            logger.info(f'Contact Deleted {selected}')
            self.messages.information(self, 'Done', 'Contact Deleted.')
            item.close()
            # Если удалён активный пользователь, то деактивируем поля ввода.
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    # Функция отправки собщения пользователю.
    def send_message(self):
        # Текст в поле, проверяем что поле не пустое затем забирается сообщение и поле очищается
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        try:
            print(f'sending_message  from: {self.transport.username}  , to: {self.current_chat} , messg : {message_text}')
            self.transport.sdb_send_text_message(self.current_chat, message_text)
            self.ui.label_server_info.setText(f'Server Info: Message Sent')
            pass
        except ServerError as err:
            self.messages.critical(self, 'Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection with server lost!')
                self.close()
            self.messages.critical(self, 'Error', 'Timeout Expired!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Error', 'Connection to Server Lost!')
            self.close()
        else:
            self.database.db_message_register(self.transport.username, self.current_chat,  message_text)
            logger.debug(f'Message sent to  {self.current_chat}: {message_text}')
            self.history_list_update()

    # Слот приёма нового сообщений
    @pyqtSlot(str)
    def message(self, sender):
        self.ui.label_server_info.setText(f'Server Info: Got Incoming message')
        if sender == self.current_chat:
            self.history_list_update()

        else:
            # Проверим есть ли такой пользователь у нас в контактах:
            if self.database.db_check_contact(sender):
                # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
                if self.messages.question(self, 'Got new message', \
                                          f'Got new message from {sender}, start chat with him??', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # Раз нету,спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(self, 'New Message', \
                                          f'Got new message from {sender}.\n '
                                          f'This user is not in your Contact-list.\n '
                                          f'Add him to Contact-list and start chat?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.database.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    # Слот потери соединения
    # Выдаёт сообщение о ошибке и завершает работу приложения
    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Connection Error', 'Connection to Server Lost. ')
        self.ui.label_connection.setText(f'Connection: Disconnected')
        time.sleep(1)
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)

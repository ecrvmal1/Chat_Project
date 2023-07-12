# -*- coding: utf-8 -*-
from os.path import join

# Form implementation generated from reading ui file 'client_gui1.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
import os

dir_path = os.getcwd()
logo_filename = os.path.join(dir_path, 'client' , "logo.jpg")

class Ui_MainClientWindow(object):
    def setupUi(self, MainClientWindow):
        MainClientWindow.setObjectName("MainClientWindow")
        MainClientWindow.resize(756, 534)
        MainClientWindow.setMinimumSize(QtCore.QSize(756, 534))
        self.centralwidget = QtWidgets.QWidget(MainClientWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_contacts = QtWidgets.QLabel(self.centralwidget)
        self.label_contacts.setGeometry(QtCore.QRect(20, 80, 101, 16))
        self.label_contacts.setObjectName("label_contacts")
        self.btn_add_contact = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_contact.setGeometry(QtCore.QRect(20, 340, 121, 31))
        self.btn_add_contact.setObjectName("btn_add_contact")
        self.btn_remove_contact = QtWidgets.QPushButton(self.centralwidget)
        self.btn_remove_contact.setGeometry(QtCore.QRect(150, 340, 121, 31))
        self.btn_remove_contact.setObjectName("btn_remove_contact")
        self.label_history = QtWidgets.QLabel(self.centralwidget)
        self.label_history.setGeometry(QtCore.QRect(310, 10, 391, 21))
        self.label_history.setObjectName("label_history")
        self.text_message = QtWidgets.QTextEdit(self.centralwidget)
        self.text_message.setGeometry(QtCore.QRect(300, 360, 441, 71))
        self.text_message.setObjectName("text_message")
        self.label_new_message = QtWidgets.QLabel(self.centralwidget)
        self.label_new_message.setGeometry(QtCore.QRect(300, 330, 250, 16))
        self.label_new_message.setObjectName("label_new_message")
        self.list_contacts = QtWidgets.QListView(self.centralwidget)
        self.list_contacts.setGeometry(QtCore.QRect(10, 110, 251, 211))
        self.list_contacts.setObjectName("list_contacts")
        self.list_messages = QtWidgets.QListView(self.centralwidget)
        self.list_messages.setGeometry(QtCore.QRect(300, 40, 441, 281))
        self.list_messages.setObjectName("list_messages")
        self.btn_send = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send.setGeometry(QtCore.QRect(610, 450, 131, 31))
        self.btn_send.setObjectName("btn_send")
        self.btn_clear = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear.setGeometry(QtCore.QRect(460, 450, 131, 31))
        self.btn_clear.setObjectName("btn_clear")
        # self.label_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_logo = QLabel(self.centralwidget)
        self.label_logo.setGeometry(QtCore.QRect(90, 390, 101, 81))
        pixmap = QPixmap(logo_filename)
        self.label_logo.setPixmap(pixmap)
        self.label_logo.setOpenExternalLinks(False)
        self.label_logo.setObjectName("label_logo")
        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(20, 30, 201, 17))
        self.label_username.setObjectName("label_username")

        MainClientWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainClientWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 756, 25))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainClientWindow.setMenuBar(self.menubar)

        self.statusBar = QtWidgets.QStatusBar(MainClientWindow)
        self.statusBar.setObjectName("statusBar")

        self.label_connection = QtWidgets.QLabel(self.statusBar)
        self.label_connection.setMaximumWidth(200)
        self.label_connection.setObjectName("label_connection")

        self.label_server_info = QtWidgets.QLabel(self.statusBar)
        self.label_server_info.setMaximumWidth(300)
        self.label_server_info.setObjectName("label_server_info")

        widget = QWidget()
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.label_connection)
        widget.layout().addWidget(self.label_server_info)
        self.statusBar.addWidget(widget, 1)

        MainClientWindow.setStatusBar(self.statusBar)
        self.menu_exit = QtWidgets.QAction(MainClientWindow)
        self.menu_exit.setObjectName("menu_exit")
        self.menu_add_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_add_contact.setObjectName("menu_add_contact")
        self.menu_del_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_del_contact.setObjectName("menu_del_contact")
        self.menu.addAction(self.menu_exit)
        self.menu_2.addAction(self.menu_add_contact)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_2.addSeparator()
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainClientWindow)
        self.btn_clear.clicked.connect(self.text_message.clear)
        QtCore.QMetaObject.connectSlotsByName(MainClientWindow)

    def retranslateUi(self, MainClientWindow):
        _translate = QtCore.QCoreApplication.translate
        MainClientWindow.setWindowTitle(_translate("MainClientWindow", "Async Chat  Terminal                   BetaVersion"))
        self.label_contacts.setText(_translate("MainClientWindow", "Contacts"))
        self.btn_add_contact.setText(_translate("MainClientWindow", "Add Contact"))
        self.btn_remove_contact.setText(_translate("MainClientWindow", "Del Contact"))
        self.label_history.setText(_translate("MainClientWindow", "Messages:"))
        self.label_new_message.setText(_translate("MainClientWindow", "New message:"))
        self.btn_send.setText(_translate("MainClientWindow", "Send message"))
        self.btn_clear.setText(_translate("MainClientWindow", "Clear"))
        self.label_username.setText(_translate("MainClientWindow", "Username"))
        self.label_connection.setText(_translate("MainClientWindow", "Connection:"))
        self.label_server_info.setText(_translate("MainClientWindow", "Server Info: "))
        self.menu.setTitle(_translate("MainClientWindow", "File"))
        self.menu_2.setTitle(_translate("MainClientWindow", "Contacts"))
        self.menu_exit.setText(_translate("MainClientWindow", "Exit"))
        self.menu_add_contact.setText(_translate("MainClientWindow", "Add Contact"))
        self.menu_del_contact.setText(_translate("MainClientWindow", "Delete Contact"))

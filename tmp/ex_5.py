"""Обработчики событий, связанных с элементами интерфейса"""

import sys
from PyQt5 import QtWidgets


def on_clicked(my_param):
    print("Кнопка нажата. Функция on_clicked")


class MyClass:

    def __init__(self, x=0):
        self.x = x

    def __call__(self):
        print("Кнопка нажата. Метод MyClass.__call__()")
        print("x = ", self.x)

    def on_clicked(self):
        print("Кнопка нажата. Метод MyClass.on_clicked()")


OBJ = MyClass()
APP = QtWidgets.QApplication(sys.argv)
BUTTON = QtWidgets.QPushButton("Нажми меня")

# В качестве обработчика назначается функция
BUTTON.clicked.connect(lambda: on_clicked('текст'))

# В качестве обработчика назначается метод объекта
BUTTON.clicked.connect(OBJ.on_clicked)

# В качестве обработчика назначается экземпляр класса
BUTTON.clicked.connect(MyClass(10))

# В качестве обработчика назначается lambda-функция
BUTTON.clicked.connect(lambda: MyClass(5)())

BUTTON.show()
sys.exit(APP.exec_())

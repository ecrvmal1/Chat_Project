"""
Подключаем Python-файл с разметкой интерфейса.
Этот файл мы получили через утилиту pyuic.
Пример использования этой утилиты:
pyuic5 test.ui -o test.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, qApp
import test

APP = QApplication(sys.argv)
WINDOW_OBJ = QWidget()
UI = test.Ui_Form()
UI.setupUi(WINDOW_OBJ)
UI.pushButton_2.clicked.connect(qApp.quit)
WINDOW_OBJ.show()
sys.exit(APP.exec_())

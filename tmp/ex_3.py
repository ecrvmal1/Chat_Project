"""Простейшее окно, создаем вручную с помощью кода"""

import sys
# QtWidgets — содержит классы для классических приложений
# на основе виджетов, модуль выделен из QtGui в Qt 5
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget

if __name__ == '__main__':
    """
    Каждое приложение PyQt5 должно создать объект приложения (экземпляр QApplication). 
    Параметр sys.argv это список аргументов командной строки. 
    Скрипты Python можно запускать из командной строки. 
    Это способ, которым мы можем контролировать запуск наших сценариев.
    """
    app = QApplication(sys.argv)

    # Класс QWidget - это базовый класс для всех объектов пользовательского интерфейса
    w = QWidget()
    # Определяем размеры виджета
    w.resize(250, 150)
    # Позиционируем виджет
    w.move(800, 400)
    # Заголовок виджета
    w.setWindowTitle('Simple')
    # Отобразить окно
    w.show()

    screen = QDesktopWidget().screengeometry()
    x = int((screen.width()-w.width())/2)
    y = int((screen.width()-w.width())/2)
    w.move(x,y)           # run the app



    # Запуск приложения
    sys.exit(app.exec_())

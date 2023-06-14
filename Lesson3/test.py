"""Данный вариант будет рабоать только у меня(ну может еще у кого запустится)"""


import os
import queue
import subprocess
import time

import psutil

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        catalog = os.getcwd()
        # p = f'/usr/bin/python3.8 {catalog}/client.py -m send -u user'
        p = f'python3  {catalog}/client.py -m listen -u user22; bash'
        # PROCESS.append(subprocess.Popen(['konsole', '-e', p]))
        # PROCESS.append(subprocess.call(['open', '-W', '-a', 'Terminal.app', 'python', '--args', 'bb.py']))
        # PROCESS.append(subprocess.Popen(['gnome-terminal',
        #                                  '--',
        #                                  # 'bash',
        #                                  # '-e',s

        #                                  'python3 /home/user1/Desktop/chat/Lesson3/client.py']))
        #  /home/user1/Desktop/chat/Lesson3/client.py
        PROCESS.append(subprocess.Popen(["gnome-terminal", "--", "sh", "-c", p]))
        print(p)
        time.sleep(0.1)

    elif ACTION == 'x':
        for p in psutil.process_iter():
            # print(p)
            if 'gnome-terminal' in p.name():
                print(p)
                p.terminate()
                p.wait()
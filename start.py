""" SERVER - CLIENT LAUNCHER FOR LINUX """


import os
import subprocess
import psutil
import time

PROCESS = []

while True:
    ACTION = input('Выберите действие:  '
                   's - запустить сервер ,' 
                   'c - запустить клиенты,' 
                   'x - закрыть все окна: '
                   'q - выход \n')

    if ACTION == 's':
        catalog = os.getcwd()
        p = f'python "{catalog}/server.py"'
        PROCESS.append(subprocess.Popen(["gnome-terminal", "--", "sh", "-c", p]))
        print(p)
        time.sleep(0.1)

    elif ACTION == 'c':
        catalog = os.getcwd()
        for i in range(1, 3):
            # print(i)
            # p = f'python {catalog}/client.py -m send -u userS{i}'
            p = f'python {catalog}/client.py -u user{i}'
            PROCESS.append(subprocess.Popen(["gnome-terminal", "--", "sh", "-c", p]))
            print(p)
            time.sleep(1)

    elif ACTION == 'x':
        for p in psutil.process_iter():
            if 'gnome-terminal' in p.name():
                print(f'Process ended {p.name} {p.pid}')
                p.terminate()
                p.wait()

    elif ACTION == 'q':
        break

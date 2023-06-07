import os
from subprocess import Popen, call, PIPE
import psutil

p_list = []  # Список клиентских процессов

while True:
    user = input("Запустить 10 клиентов (s) \n"
                 "Закрыть клиентов (x) \n"
                 "Выйти (q) \n")

    if user == 'q':
        break
    elif user == 's':
        for _ in range(2):
            # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
            # чтобы каждый процесс запускался в отдельном окне консоли
            # p_list.append(Popen(['python3', 'client.py'],
                                # creationflags=CREATE_NEW_CONSOLE))

            My_Cmmnd = "python3 client.py; bash"
            # p_list.append(os.system("gnome-terminal -e 'bash -c \"" + My_Cmmnd + ";bash\"'"))
            os.system('gnome-terminal -- bash -c "python3 client.py; bash -i" ')
        print(' Запущено 10 клиентов')
    elif user == 'x':
        # for p in p_list:
        #     p.kill()
        # p_list.clear()
        for p in psutil.process_iter():
            print(p.name)
            # if 'bash' in p.name():
            #     print(p.name)
                # p.terminate()
                # p.kill()
                # p.wait()
                # print(p.name)

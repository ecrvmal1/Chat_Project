"""
 Написать функцию host_ping(),
 в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
 Аргументом функции является список, в котором каждый сетевой узел должен быть представлен
 именем хоста или ip-адресом.
 В функции необходимо перебирать ip-адреса и проверять их доступность
 с выводом соответствующего сообщения («Узел доступен», «Узел недоступен»).
 При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().

 script listing at lines: 54...80
"""
import ipaddress
import subprocess
from tabulate import tabulate
from term import saveCursor, restoreCursor

# addresses = ['87.250.251.119', 'www.google.com', 'www.rambler.ru', '192.168.1.1', 'www.yandex.ru']


def host_ping(addresses, ping_attempts=3, echo=True):

    addresses_available =[]
    addresses_not_available = []
    addresses_len = len(addresses)

    if not echo:
        saveCursor()

    for i in range(addresses_len):
        address = addresses.pop(0)
        try:
            address = ipaddress.ip_address(address)
        except ValueError:
            pass
        subproc_ping = subprocess.Popen(["ping", '-c', f'{ping_attempts}', f'{address}'],
                                        shell=False, stdout=subprocess.PIPE)
        subproc_ping.wait()
        if subproc_ping.returncode == 0:
            addresses_available.append(f'{address}')
            if echo:
                print(f'address {address} Доступен')
        else:
            addresses_not_available.append(f'{address}')
            if echo:
                print(f'address {address} Не доступен')

        subproc_ping.kill()
        subproc_ping.wait()
        if not echo:
            progress = int(i/(addresses_len-1)*100)
            print(f'Completed {progress} %', end='')
            restoreCursor()

    return addresses_available, addresses_not_available


if __name__ == '__main__':
    list_addresses = ['ya111.ru', '87.250.251.119', '192.168.1.1', 'google.com', '8.8.8.8', 'yandex.ru']
    addr_ok, addr_not_ok = host_ping(list_addresses)
    print('\n Доступны адреса : \n', tabulate(addr_ok))
    print('\n Недоступны адреса :\n', tabulate(addr_not_ok))


"""
/home/user1/Desktop/chat/venv/bin/python /home/user1/Desktop/chat/Lesson_9/host_ping.py
address ya111.ru Не доступен
ping: ya111.ru: Name or service not known
address 87.250.251.119 Доступен
address 192.168.1.1 Доступен
address google.com Доступен
address 8.8.8.8 Доступен
address yandex.ru Доступен


 Доступны адреса :
 -  -  -  -  -  -  -  -  -  -  -  -  -  -
8  7  .  2  5  0  .  2  5  1  .  1  1  9
1  9  2  .  1  6  8  .  1  .  1
g  o  o  g  l  e  .  c  o  m
8  .  8  .  8  .  8
y  a  n  d  e  x  .  r  u
-  -  -  -  -  -  -  -  -  -  -  -  -  -

 Недоступны адреса :
 -  -  -  -  -  -  -  -
y  a  1  1  1  .  r  u
-  -  -  -  -  -  -  -

Process finished with exit code 0
"""
"""
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com
и преобразовать результаты из байтовового в строковый тип на кириллице.

used library: pip install googletrans==3.1.0a0

code output at lines 41...67
"""


import subprocess
import chardet

# args = ['ping', 'yandex.ru']
# subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
#
# for line in subproc_ping.stdout:
#     l = line.decode('utf-8')
#     print(l)

import chardet
from googletrans import Translator
translator = Translator()

cmd_list = ['ping -c 5 yandex.ru',
            'ping -c 5 google.com'
            ]

for cmd in cmd_list:
    YA_PING = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in YA_PING.stdout:
        print(f'   Type of ping answer: {type(line)}')
        result = chardet.detect(line)
        print(f"   Detected encoding       : {result['encoding']}")
        line = line.decode(result['encoding']).encode('utf-8')
        print(f"   Original ping answer : {line} ")
        print('-----------------------------------')
        translated_obj = translator.translate(line, src='en', dest='ru')
        translated_string = translated_obj.text
        print(f'    Cyrillic Output   : {translated_string}')
        print(f'    Type of Cyr_Output: {type(translated_string)}')
        print('***********************************\n')


"""
Listing:
(venv) user1@ubuntu:~/Desktop/chat/Lesson1$ python3 task5.py
   Type of ping answer: <class 'bytes'>
   Detected encoding       : ascii
   Original ping answer : b'PING yandex.ru (77.88.55.88) 56(84) bytes of data.\n' 
-----------------------------------
    Cyrillic Output   : b'PING yandex.ru (77.88.55.88) 56(84) байт данных.\n'
    Type of Cyr_Output: <class 'str'>
***********************************

   Type of ping answer: <class 'bytes'>
   Detected encoding       : ascii
   Original ping answer : b'64 bytes from yandex.ru (77.88.55.88): icmp_seq=1 ttl=54 time=12.7 ms\n' 
-----------------------------------
    Cyrillic Output   : b'64 байта с yandex.ru (77.88.55.88): icmp_seq=1 ttl=54 time=12,7 мс\n'
    Type of Cyr_Output: <class 'str'>
***********************************

   Type of ping answer: <class 'bytes'>
   Detected encoding       : ascii
   Original ping answer : b'64 bytes from yandex.ru (77.88.55.88): icmp_seq=2 ttl=54 time=12.7 ms\n' 
-----------------------------------
    Cyrillic Output   : b'64 байта с yandex.ru (77.88.55.88): icmp_seq=2 ttl=54 time=12,7 мс\n'
    Type of Cyr_Output: <class 'str'>
***********************************
"""
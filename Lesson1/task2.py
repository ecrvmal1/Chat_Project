"""
2. Каждое из слов «class», «function», «method»
записать в байтовом типе без преобразования в последовательность кодов
(не используя методы encode и decode) и определить тип,
содержимое и длину соответствующих переменных.

code output at lines 19...25
"""

WORD_1 = b'class'
WORD_2 = b'function'
WORD_3 = b'method'

WORD_LIST = [WORD_1, WORD_2, WORD_3]

for item in WORD_LIST:
    print(f"Содержимое: {item}, тип: {type(item)} , длина: {len(item)}")

"""
Code Output:
(venv) user1@ubuntu:~/Desktop/chat/Lesson1$ python3 task2.py
Содержимое: b'class', тип: <class 'bytes'> , длина: 5
Содержимое: b'function', тип: <class 'bytes'> , длина: 8
Содержимое: b'method', тип: <class 'bytes'> , длина: 6
"""


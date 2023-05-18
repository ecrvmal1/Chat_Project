"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование»,
«сокет»,
«декоратор».
Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое.

code output at lines 40...47
"""
from chardet.universaldetector import UniversalDetector

text_1 = "сетевое программирование"
text_2 = "сокет"
text_3 = "декоратор"
text_list = [text_1, text_2, text_3]

# Writing file
with open('test_file.txt', "w") as input_file:
    for item in text_list:
        input_file.write(item)
        input_file.write('\n')

# Detect encoding type
DETECTOR = UniversalDetector()
with open('test_file.txt', 'rb') as file:
    for i in file:
        DETECTOR.feed(i)
        if DETECTOR.done:
            break
    DETECTOR.close()
file_encoding = DETECTOR.result['encoding']
print(f" encoding: {file_encoding}")

# open file with correct encoding
with open('test_file.txt', 'r', encoding=file_encoding) as file:
    file_text = file.read()
print(file_text)

"""
script output:
(venv) user1@ubuntu:~/Desktop/chat/Lesson1$ python3 task6.py
 encoding: utf-8
сетевое программирование
сокет
декоратор
"""


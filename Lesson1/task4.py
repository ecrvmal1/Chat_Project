"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard»
из строкового представления в байтовое и
выполнить обратное преобразование (используя методы encode и decode).


code output at lines 38...61
"""


def print_list(input_list, header='', comment=''):
    print(f'\n *** {header} ***')
    for el in input_list:
        print(f' {comment} : {el} ')


string_1 = 'разработка'
string_2 = 'администрирование'
string_3 = 'protocol'
string_4 = 'standard'

INITIAL_LIST = [string_1, string_2, string_3, string_4]
print_list(INITIAL_LIST, "INITIAL LIST", "initial element")

encoded_list = []

for item in INITIAL_LIST:
    encoded_item=item.encode('utf-8')
    encoded_list.append(encoded_item)
print_list(encoded_list, "ENCODED LIST", "encoded element")

decoded_list = []

for item in encoded_list:
    decoded_item=item.decode('utf-8')
    decoded_list.append(decoded_item)
print_list(decoded_list, "DECODED LIST", "decoded element")

"""
SCRIPT LISTING: 

(venv) user1@ubuntu:~/Desktop/chat/Lesson1$ python3 task4.py

 *** INITIAL LIST ***
 initial element : разработка 
 initial element : администрирование 
 initial element : protocol 
 initial element : standard 

 *** ENCODED LIST ***
 encoded element : b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0' 
 encoded element : b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5' 
 encoded element : b'protocol' 
 encoded element : b'standard' 

 *** DECODED LIST ***
 decoded element : разработка 
 decoded element : администрирование 
 decoded element : protocol 
 decoded element : standard 

"""
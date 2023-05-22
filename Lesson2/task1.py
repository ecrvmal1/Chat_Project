"""
1. Задание на закрепление знаний по модулю CSV.
Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
и формирующий новый «отчетный» файл в формате CSV.

Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными,
их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы»,
«Название ОС»,
«Код продукта»,
«Тип системы».
Значения каждого параметра поместить в соответствующий список.
Должно получиться четыре списка — например,
os_prod_list,
os_name_list,
os_code_list,
os_type_list.
В этой же функции создать главный список для хранения данных отчета — например,
main_data — и поместить в него названия столбцов отчета в виде списка:
«Изготовитель системы»,
«Название ОС»,
«Код продукта»,
«Тип системы».
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Проверить работу программы через вызов функции write_to_csv().
"""

import csv
import re

file_list = ['info_1.txt', 'info_2.txt', 'info_3.txt']
DEBUG_INFO = 0


def get_data(files):
    manufacturer_list = []
    os_name_list = []
    product_code_list = []
    system_type_list = []
    main_data = []
    for file in files:
        print('filename', file)
        with open(file, 'r', encoding='utf-8') as input_file:
            file_data = input_file.read()
            # print(file_data)
            reg_exp = re.compile(r'(Изготовитель системы:)(\s*)([A-Z]+)')
            search_value = re.search(reg_exp,file_data)[3]
            manufacturer_list.append(search_value)

            reg_exp = re.compile(r'(Название ОС:)(\s*)([A-Za-z0-9А-Яа-я]+)')
            search_value = re.search(reg_exp,file_data)[3]
            os_name_list.append(search_value)

            reg_exp = re.compile(r'(Код продукта:)(\s*)([0-9]+-OEM-[0-9]+-[0-9]+)')
            search_value = re.search(reg_exp,file_data)[3]
            product_code_list.append(search_value)

            reg_exp = re.compile(r'(Тип системы:)(\s*)([A-Za-z0-9- ]+)')
            search_value = re.search(reg_exp,file_data)[3]
            system_type_list.append(search_value)

    if DEBUG_INFO:
        print('manufacturer_list', manufacturer_list)
        print('os_name_list', os_name_list)
        print('product_code_list', product_code_list)
        print('system_type_list', system_type_list)

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    for i, file in enumerate(files):
        row_data = []
        row_data.append(i+1)
        row_data.append(manufacturer_list[i])
        row_data.append(os_name_list[i])
        row_data.append(product_code_list[i])
        row_data.append(system_type_list[i])
        main_data.append(row_data)
    print('main_data: ', main_data)
    return main_data


def write_to_csv(file_name):
    computer_data = get_data(file_list)
    with open(file_name, 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in computer_data:
            f_n_writer.writerow(row)


if __name__ == '__main__':
    write_to_csv('computer_data.csv')



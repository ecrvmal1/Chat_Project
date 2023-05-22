"""
2. Задание на закрепление знаний по модулю json.
Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными.
Для этого:
Создать функцию write_order_to_json(), в которую передается 5 параметров —
товар (item),
количество (quantity),
цена (price),
покупатель (buyer),
дата (date).
Функция должна предусматривать запись данных в виде словаря в файл orders.json.
При записи данных указать величину отступа в 4 пробельных символа;

Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.

"""

import json
from datetime import date


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', "r", encoding='utf-8' ) as input_file:
        orders_data = json.load(input_file)['orders']
        # print('input data: ', orders_data)
    new_order_data = {"item": item, "quantity": quantity, "price": price, "buyer": buyer, "data": date}
    orders_data.append(new_order_data)
    orders_data = {'orders': orders_data}
    print(orders_data)

    with open('orders.json', "w", encoding='utf-8' ) as output_file:
        json.dump(orders_data, output_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    today = str(date.today())
    write_order_to_json('Processor', '5', '530', 'Иванов', today)
    write_order_to_json('Memory', '1000', '250', 'Петров', today)
    write_order_to_json('Storage', '2000', '150', 'Сидоров', '1994-01-01')
    write_order_to_json('Cooler', '1', '5', 'Козлов', '1993-12-31')






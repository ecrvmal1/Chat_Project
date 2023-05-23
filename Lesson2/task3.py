"""
### 3. Задание на закрепление знаний по модулю yaml.
Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата. Для этого:
Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список,
второму — целое число,
третьему — вложенный словарь,
где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке ASCII (например, €);

Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.

output listing at lines 35...41
"""

import yaml

data_to_write = {
    "drinks": ['rum', 'whisky', 'tequila', 'gin', 'vodka', 'cognac'],
    "total_drinks": 6,
    "drink_price": {'rum': '5\u20bf', 'whisky': '10\u20bf', 'tequila': '8\u20bf', 'gin': '16\u20bf', 'vodka': '25\u20bf', 'cognac': '150\u20bf'}
}

with open('file.yaml','w',encoding='utf-8') as output_file:
    yaml.dump(data_to_write, output_file, default_flow_style=False, allow_unicode=True)

with open('file.yaml','r',encoding='utf-8') as input_file:
    content = yaml.safe_load(input_file)
    print(content)
print("\n data written correctly : ", data_to_write == content)


"""
output listing:
{'drink_price': {'cognac': '150₿', 'gin': '16₿', 'rum': '5₿', 'tequila': '8₿', 'vodka': '25₿', 'whisky': '10₿'}, 'drinks': ['rum', 'whisky', 'tequila', 'gin', 'vodka', 'cognac'], 'total_drinks': 6}

 data written correctly :  True
"""


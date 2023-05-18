"""
3. Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе.

code output at lines 23...31
"""

WORD_1 = 'attribute'
WORD_2 = 'класс'
WORD_3 = 'функция'
WORD_4 = 'type'

WORD_LIST = [WORD_1, WORD_2, WORD_3, WORD_4]

for item in WORD_LIST:
    try:
        byte_word = bytes(item,'ascii')
        print(f'Слово "{item}" возможно конвертировать в bytes : {byte_word}')
    except UnicodeEncodeError:
        print(f'Слово "{item}" невозможно конвертировать в bytes')


"""
Code listing

Слово "attribute" возможно конвертировать в bytes : b'attribute'
Слово "класс" невозможно конвертировать в bytes
Слово "функция" невозможно конвертировать в bytes
Слово "type" возможно конвертировать в bytes : b'type'

"""

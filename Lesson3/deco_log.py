import inspect
import logging
import sys
import traceback
from functools import wraps

# print(sys.argv)     # returns ['client.py']    or  ['server.py']

if sys.argv[0].find('client') == -1:
    # if not find 'client'
    LOGGER = logging.getLogger('server_logger')
else:
    LOGGER = logging.getLogger('client_logger')


def log(func):
    """Функция-декоратор"""
    def log_saver(*args, **kwargs):
        """Обертка"""
        spaces = 57 * " "
        result = func(*args, **kwargs)
        # print(f'traceback : {traceback.format_stack()}')
        # print(f'stack : {inspect.stack()}')
        LOGGER.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func.__module__}. Вызов из'
                     f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return result
    return log_saver

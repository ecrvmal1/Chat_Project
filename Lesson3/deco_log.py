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
        LOGGER.debug(f' called function {func.__name__} with params: {args}, {kwargs}. '
                     f' called from module  {func.__module__}.' 
                     f' called from function {traceback.format_stack()[0].strip().split()[-1]}.'
                     f' called from function {inspect.stack()[1][3]}', stacklevel=2)
        return result
    return log_saver

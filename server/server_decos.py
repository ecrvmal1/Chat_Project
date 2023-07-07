import socket
import logging
import sys

sys.path.append('../')
import log.client_log_config
import log.server_log_config

# метод определения модуля, источника запуска.
if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    logger = logging.getLogger('server_logger')
else:
    # иначе сервер
    logger = logging.getLogger('client_logger')


def log(func_to_log):
    '''
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функиции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    '''

    def log_saver(*args, **kwargs):
        logger.debug(
            f' Called function: {func_to_log.__name__} with params: {args} , {kwargs}. Call from Module {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver


def login_required(func):
    '''
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    '''

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр ServerMessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server.server_core import ServerMessageProcessor
        from server.server_variables import ACTION, PRESENCE
        if isinstance(args[0], ServerMessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке user_list класса
                    # ServerMessageProcessor
                    for client in args[0].user_list:
                        if args[0].user_list[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

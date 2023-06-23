""" Constants """

import logging

DEFAULT_CLIENT_PORT = 7777
DEFAULT_CLIENT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
SENDER = 'sender'
FROM = 'from'
TO = 'to'
EXIT = 'exit'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
STATUS = 'status'
TYPE = 'type'


# Logging
# Logging levels
FILE_LOGGING_LEVEL = logging.DEBUG
TERMINAL_LOGGING_LEVEL = logging.DEBUG

RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

""" Constants """

import logging

DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
SERVER_DATABASE = 'sqlite:///server_db.db3'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
DEFAULT_USERNAME = 'user'
FROM = 'from'
TO = 'to'
SENDER = 'sender'
EXIT = 'exit'
ADD_CONTACT = 'add_contact'
REMOVE_CONTACT = 'remove_contact'
USERS_REQUEST = 'users_request'
CONTACT = 'contact'
PUBLIC_KEY_REQUEST = 'pubkey_request'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
ERROR = 'error'
STATUS = 'status'
TYPE = 'type'
DATA = 'data'
GET_CONTACTS = 'get_contacts'
DATA_LIST = 'data_list'

# Logging
# Logging levels
FILE_LOGGING_LEVEL = logging.DEBUG
TERMINAL_LOGGING_LEVEL = logging.DEBUG

RESPONSE_200 = {'action': 'response', 'response': 200}
RESPONSE_202 = {'action': 'response', 'response': 202}
RESPONSE_205 = {'action': 'response', 'response': 205}
RESPONSE_400 = {'action': 'response', 'response': 400, 'error': 'bad request'}
RESPONSE_511 = {'action': 'response', 'response': 511}

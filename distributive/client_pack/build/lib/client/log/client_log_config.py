# client_log_config #

import sys
import os
import logging.handlers
import logging

sys.path.append('../Lesson3/')
from client.client_variables import FILE_LOGGING_LEVEL, TERMINAL_LOGGING_LEVEL


# formatting depending on logging.LEVEL below:


LOG_FILE_PATH = os.getcwd()
LOG_FILE_NAME = os.path.join(LOG_FILE_PATH, 'log', 'logs', 'client', 'client.log')

LOGGER = logging.getLogger('client_logger')

LOGGER_FORMATTER = logging.Formatter('%(asctime)-16s %(levelname)-10s %(filename)-22s %(module)-14s %(funcName)s %(message)s')


STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(LOGGER_FORMATTER)
STREAM_HANDLER.setLevel(TERMINAL_LOGGING_LEVEL)

FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf8')

# FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_FILE_NAME,
#                                                          encoding = 'UTF-8',  interval=1, when='M',
#                                                          backupCount=10, delay = True)
FILE_HANDLER.setFormatter(LOGGER_FORMATTER)
FILE_HANDLER.setLevel(FILE_LOGGING_LEVEL)

LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.DEBUG)


if __name__ == '__main__':
    LOGGER.debug('test debug message')
    LOGGER.info('test info message')
    LOGGER.error('test error message')
    LOGGER.critical('test critical message')
# server_log_config #

import sys
import os
import logging
import logging.handlers

sys.path.append('../')
from common.server_variables import FILE_LOGGING_LEVEL, TERMINAL_LOGGING_LEVEL


# formatting depending on logging.LEVEL below:
class Formatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            self._style._fmt = '%(asctime)-16s %(levelname)-10s %(message)s'
        else:
            self._style._fmt = '%(asctime)-16s %(levelname)-10s %(filename)-22s %(module)-14s %(funcName)s %(message)s'
        return super().format(record)


LOG_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = os.path.join(LOG_FILE_PATH, 'logs', 'server', 'server.log')

LOGGER = logging.getLogger('server_logger')

# LOGGER_FORMATTER = logging.Formatter('%(asctime)-16s %(levelname)-10s %(filename)-22s %(module)-14s %(funcName)s %(message)s')
LOGGER_FORMATTER = Formatter()

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(LOGGER_FORMATTER)
STREAM_HANDLER.setLevel(TERMINAL_LOGGING_LEVEL)

# FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf8')

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_FILE_NAME,
                                                         encoding='UTF-8',  interval=1, when='M',
                                                         backupCount=10,
                                                         # delay=True
                                                         )
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

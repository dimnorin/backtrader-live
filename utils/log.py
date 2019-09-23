import sys
import logging
import logging.handlers
import threading
from concurrent.futures import ThreadPoolExecutor


class Logger(object):
    def __init__(self, log_lvl=logging.DEBUG, stream=None):
        self._terminal = stream
        self._init_logger(log_lvl)
        self._upd_listeners = []
        self._executor = ThreadPoolExecutor(max_workers=2)

    def _init_logger(self, log_lvl):
        log_handler = logging.handlers.RotatingFileHandler('backtrader.log', maxBytes=1024 * 1024, backupCount=3)
        self._formatter = logging.Formatter('%(asctime)s: %(message)s', '%b %d %H:%M:%S')
        log_handler.setFormatter(self._formatter)
        self._logger = logging.getLogger()
        self._logger.addHandler(log_handler)
        self._logger.setLevel(log_lvl)

        sys.excepthook = self._handle_exception

    def _notify(self, msg):
        # threading.Thread(target=self._notify_threaded, args=(msg)).start()
        self._executor.submit(self._notify_threaded, (msg))

    def _notify_threaded(self, msg):
        for listener in self._upd_listeners:
            listener.notify(msg)

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        exc_info = (exc_type, exc_value, exc_traceback)
        self._print_ex(exc_info)
        self._logger.error("Uncaught exception", exc_info=exc_info)
        # self._notify(self._formatter.formatException(exc_info))
        self._notify(str(exc_info))

    def write(self, message):
        if self._logger.getEffectiveLevel() == logging.DEBUG and self._terminal:
            self._terminal.write(message)
        self._logger.debug(message)

    def _print_ex(self, exc_info):
        if self._terminal:
            self._terminal.write('Traceback:%s\n' % self._formatter.formatException(exc_info))

    # def format_last_ex(self):
    #     exc_info = list(sys.exc_info())
    #     return 'Traceback:%s\n' % self._formatter.formatException(exc_info)

    def getLogger(self):
        return self._logger

    def add_upd_listener(self, upd_listener):
        self._upd_listeners.append(upd_listener)

    def info(self, message, not_notify=False):
        if self._terminal:
            self._terminal.write('%s\n' % message)
            self._terminal.flush()
        self._logger.info(message)
        if not not_notify:
            self._notify(message)

    def error(self, e: Exception = None):
        if e:
            self._logger.exception(e)
            self._notify(str(e))
        else:
            exc_info = list(sys.exc_info())
            self._handle_exception(*exc_info)

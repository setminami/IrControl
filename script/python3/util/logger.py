import logging, pytz
from datetime import datetime
from os import path
from pythonjsonlogger import jsonlogger
from util import is_debug, _BASE


# for avoid virtualenv
JSON_LOGGING_PATH = path.normpath(path.join(_BASE, '../../../../log/SunLight.json'))


class JsonLoggerFormatter(jsonlogger.JsonFormatter):
    """
    https://github.com/madzak/python-json-logger#customizing-fields
    """
    def add_fields(self, log_record, record, message_dict):
        super(JsonLoggerFormatter, self).add_fields(log_record, record, message_dict)
        print(log_record)
        # e.g., log_record = OrderedDict([('asctime', '2018-.....+0900'), ('levelname', 'INFO'), ...])
        asctime = log_record.pop('asctime', None)
        if asctime is not None:
            # this doesn't use record.created, so it is slightly off
            log_record['timestamp'] = asctime
        else:
            log_record['logging_error'] = 'asctime not found! timezone has been applied UTC, forcely.'
            log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        lv = log_record.pop('levelname', None)
        if lv is not None:
            log_record['level'] = lv.upper()
        else:
            log_record['level'] = record.levelname

        exc_info = log_record.pop('exc_info', None)
        # ∵ original exc_info convert to null
        if exc_info is not None:
            log_record['exc_info'] = exc_info
            # if It caught emergency status, add below.
            d_f = lambda x: x
            for emerge_key, f in [('stack_info', d_f), ('pathname', lambda p: os.path.basename(p)), ('line_no', d_f)]:
                log_record[emerge_key] = f(eval(f'record.{emerge_key}'))


def module_logger(modname):
    """ IF for external """
    log = logging.getLogger(modname)
    handler = logging.StreamHandler()
    json_handler = logging.FileHandler(JSON_LOGGING_PATH)
    formatter = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s] %(message)s', datefmt='%y%m%dT%H%M%S%z')
    handler.setFormatter(formatter)
    # JsonFormatter inherit from logging.Formatter
    json_formatter = JsonLoggerFormatter('(asctime) (levelname) (name) (message) (exc_info) (processName) \
                                            (threadName) (thread)', datefmt='%Y-%m-%dT%H:%M:%S%z')
    json_handler.setFormatter(json_formatter)
    log.addHandler(handler)
    log.addHandler(json_handler)
    log.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    return log


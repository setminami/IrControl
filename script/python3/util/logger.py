import logging, pytz
from datetime import datetime
from util import is_debug, JSON_LOGGING_PATH


def module_logger(modname, file_path=JSON_LOGGING_PATH):
    """ IF for external """
    log = logging.getLogger(modname)
    handler = logging.FileHandler(file_path, 'a')
    # 1-log represented by 1-json literal dict
    formatter = logging.Formatter('{"timestamp": {"time": "%(asctime)s", "msecs": %(msecs)d}}, ' +
                                    '"loglevel": "%(levelname)s", "message": "%(message)s", ' +
                                    '"caller": {"call_from": "%(name)s.%(funcName)s()", ' +
                                    '"file": "%(filename)s", "line_no": "%(lineno)s"}, ' +
                                    '"runtime": {"process_id": %(process)d, "thread_name": "%(threadName)s", ' +
                                    '"thread_id": %(thread)d}},',
                                    datefmt='%Y-%m-%d %H:%M:%S%z')
    handler.setFormatter(formatter)
    # JsonFormatter inherit from logging.Formatter
    # json_formatter = JsonLoggerFormatter('(asctime) (levelname) (name) (message) (exc_info) (processName) \
    #                                        (threadName) (thread)', datefmt='%Y-%m-%dT%H:%M:%S%z')
    # json_handler.setFormatter(json_formatter)
    log.addHandler(handler)
    # log.addHandler(json_handler)
    log.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    return log


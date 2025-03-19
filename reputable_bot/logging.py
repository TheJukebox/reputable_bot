import logging
import sys
import datetime

INFO = logging.INFO
DEBUG = logging.DEBUG
WARN = logging.WARN
WARNING = logging.WARNING
ERROR = logging.ERROR

class ReputablebotFormatter(logging.Formatter):

    def colour(self, level):
        if level == "INFO":
            return "\033[92mINFO\033[0m"
        if level == "DEBUG":
            return "\033[94mDEBUG\033[0m"
        if level == "WARNING":
            return "\033[93mWARNING\033[0m"
        if level == "ERROR":
            return "\033[91mERROR\033[0m"

    def format(self, record):
        timestamp: str = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
        level = self.colour(record.levelname)
        return f"{timestamp} {record.name}: {level}: {record.msg}"

def setup_log(
    name: str,
):
    log: logging.Logger = logging.getLogger(name)
    formatter: ReputablebotFormatter = ReputablebotFormatter()

    stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

    return log

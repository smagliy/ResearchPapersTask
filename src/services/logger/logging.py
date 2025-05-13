import logging
import sys


class LoggerConfig:
    @staticmethod
    def set_up_logger(name=__name__):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.propagate = True
        return logger
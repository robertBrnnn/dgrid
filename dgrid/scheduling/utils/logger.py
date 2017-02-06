"""
Main logging class for DGrid.
"""
import logging
import sys
from dgrid.conf import settings


class _LessThanFilter(logging.Filter):
    """
    Copied from stackoverflow.com/a/31459386/4345813
    """
    def __init__(self, exclusive_maximum, name=""):
        super(_LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0


class Logger:
    """
    Used to create the logger used during execution
    """
    def __init__(self, cli_debug):
        self.cli_debug = cli_debug
        self.settings_debug = settings.DEBUG

    def get_logger(self):
        """
        Checks whether logger is set to debug, or not, and configures a logger.
        :return: required logger configuration
        """

        if self.settings_debug or self.cli_debug:
            logger = logging.getLogger()
            logger.setLevel(logging.NOTSET)

            logging_handler_out = logging.StreamHandler(sys.stdout)
            logging_handler_out.setLevel(logging.DEBUG)
            logging_handler_out.addFilter(_LessThanFilter(logging.WARNING))

            formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            logging_handler_out.setFormatter(formatter)
            logger.addHandler(logging_handler_out)

            logging_handler_err = logging.StreamHandler(sys.stderr)
            logging_handler_err.setLevel(logging.WARNING)
            logging_handler_err.setFormatter(formatter)
            logger.addHandler(logging_handler_err)
        else:
            logger = logging.getLogger()
            logger.setLevel(logging.NOTSET)

            logging_handler_out = logging.StreamHandler(sys.stdout)
            logging_handler_out.setLevel(logging.INFO)
            logging_handler_out.addFilter(_LessThanFilter(logging.WARNING))
            logger.addHandler(logging_handler_out)

            logging_handler_err = logging.StreamHandler(sys.stderr)
            logging_handler_err.setLevel(logging.WARNING)
            logger.addHandler(logging_handler_err)
        return logger

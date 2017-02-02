import logging


class LessThanFilter(logging.Filter):
    """
    Copied from stackoverflow.com/a/31459386/4345813
    """
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0
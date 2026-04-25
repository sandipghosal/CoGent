import logging
import sys


# class CustomFormatter(logging.Formatter):
#     grey = "\x1b[38;20m"
#     yellow = "\x1b[33;20m"
#     red = "\x1b[31;20m"
#     bold_red = "\x1b[31;1m"
#     reset = "\x1b[0m"
#     name = "CoGent"
#     # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
#     format = "%(name)s - %(levelname)s : %(message)s"

#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#     }

#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)
    

class CustomFormatter(logging.Formatter):
    '''
    Logging Formatter with ANSI Colors
    '''

    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"
    

def getlogger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    '''
    Configure and return a colorized logger
    '''

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)

    # file handler
    fh = logging.FileHandler('cogent')
    fh.setLevel(level)

    formatter = CustomFormatter(
        "%(filename)-20s %(lineno)4d - %(levelname)-8s :: %(message)s"
    )

    # formatter = ColorFormatter(
    #     "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
    #     datefmt="%H:%M:%S",
    # )

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
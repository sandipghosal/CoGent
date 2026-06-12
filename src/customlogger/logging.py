import logging
import sys
import itertools
import shutil

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

    lineno = itertools.count(1)
    
    def format(self, record: logging.LogRecord) -> str:
        # global line no.
        record.seq = next(CustomFormatter.lineno)

        # dynamic terminal width
        width = shutil.get_terminal_size(fallback=(120, 20)).columns

        color = self.COLORS.get(record.levelno, self.RESET)
        base_msg = super().format(record)

        # Split prefix and message
        if "::" in base_msg:
            prefix, msg = base_msg.split("::", 1)
            prefix = prefix.rstrip() + " ::"
            msg = msg.strip()
        else:
            prefix = ""
            msg = base_msg

        # Compute indent
        indent = " " * (len(prefix) + 1 if prefix else 0)

        # Split message into items
        items = [item.strip() for item in msg.split(",") if item.strip()]

        lines = []
        current_line = ""

        
        for item in items:
            # Decide if we need comma prefix
            addition = item if not current_line else ", " + item

            # Check if adding exceeds width
            if len(prefix) + 1 + len(current_line) + len(addition) > width:
                if current_line: lines.append(current_line)
                current_line = item
            else:
                current_line = item if not current_line else current_line + addition

        if current_line:
            lines.append(current_line)

        # Construct final output WITHOUT leading comma
        if not lines:
            wrapped = msg
        else:          
            wrapped = ",\n".join(
                [lines[0]] + [indent + line for line in lines[1:]]
            )
    
        if prefix:
            message = f"{prefix} {wrapped}"
        else:
            message = wrapped
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
        "%(seq)5d %(filename)-28s %(lineno)4d - %(levelname)-8s :: %(message)s"
        # "%(filename)-30s %(lineno)4d - %(levelname)-8s :: %(message)s"
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
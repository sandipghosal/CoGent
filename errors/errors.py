import logging
import sys
from pprint import pp


class Error(Exception):
    def __init__(self, message=None):
        self.message = f'{self.__class__.__name__}: {message}'
        logging.error(self.message)
        sys.exit(0)


class InvalidToken(Error):
    def __init__(self, message=None):
        super().__init__(message=message)


class InputsNotFound(Error):
    def __init__(self, message=None):
        super().__init__(message=message)


class InvalidInputFile(Error):
    def __init__(self, message=None):
        super().__init__(message=message)
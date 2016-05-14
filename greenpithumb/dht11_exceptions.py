#Custom exceptions for DHT11 sensor


class Error(Exception):
    pass


class MissingDataError(Error):
    pass


class IncorrectCRCError(Error):
    pass

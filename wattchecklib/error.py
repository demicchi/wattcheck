class SocketNotAvailableError(Exception):
    pass


class UnexpectedDataReceivedError(Exception):
    pass


class InvalidCrcError(UnexpectedDataReceivedError):
    pass


class DataDroppedError(UnexpectedDataReceivedError):
    pass


class InvalidResponseError(UnexpectedDataReceivedError):
    pass


class SetNameFailedError(UnexpectedDataReceivedError):
    pass


class FailureMessageReceivedError(UnexpectedDataReceivedError):
    pass


class GetMeasurementFailedError(UnexpectedDataReceivedError):
    pass

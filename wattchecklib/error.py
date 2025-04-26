class SocketNotAvailableError(Exception):
    """
    Internal error. Socket is not prepared.
    """
    pass


class UnexpectedDataReceivedError(Exception):
    """
    Generic error. The received data are invalid.
    """
    pass


class InvalidCrcError(UnexpectedDataReceivedError):
    """
    CRC is invalid.
    """
    pass


class DataDroppedError(UnexpectedDataReceivedError):
    """
    The length of the received message does not match the length expected.
    """
    pass


class InvalidResponseError(UnexpectedDataReceivedError):
    """
    Generic error. The command returned does not match the command sent.
    """
    pass


class SetNameFailedError(UnexpectedDataReceivedError):
    """
    Failed to set the device name.
    """
    pass


class FailureMessageReceivedError(UnexpectedDataReceivedError):
    """
    Generic error. Status code is not valid.
    """
    pass


class GetMeasurementFailedError(UnexpectedDataReceivedError):
    """
    Something wrong when trying to get measurements.
    """
    pass


class MeasurementNotReadyError(GetMeasurementFailedError):
    """
    The device is currently unable to return measurements.
    """
    pass


class ClockNotAvailableError(GetMeasurementFailedError):
    """
    The device has never gotten the current time since boot up, maybe no Internet connection?
    """
    pass


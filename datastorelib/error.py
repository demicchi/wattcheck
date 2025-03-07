class DataSaveError(Exception):
    pass


class DbConnectError(DataSaveError):
    pass


class DbNotAvailableError(Exception):
    pass

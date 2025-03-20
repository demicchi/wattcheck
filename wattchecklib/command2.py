from datetime import datetime

from .command import Command


# for RS-WFWATTCH2
class Command2(Command):
    def __init__(self, ip: str, port: int = 60121):
        super().__init__(ip, port)
    
    def get_name(self) -> str:
        # RS-WFWATTCH2 returns its name with an unnecessary null character, maybe a firmware's bug?
        return super().get_name().rstrip('\x00')
    
    # Overrides the parsing rule used in super().get_measurement()
    @staticmethod
    def parse_timestamp(raw_data: bytes) -> datetime:
        return datetime(raw_data[5] + 2000, raw_data[4], raw_data[3], raw_data[2], raw_data[1], raw_data[0])
    
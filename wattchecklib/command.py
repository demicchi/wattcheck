import functools
import inspect
import socket
import time
from collections.abc import Callable
from datetime import datetime
from typing import Concatenate

from .error import *


# for RS-WFWATTCH1
class Command:
    _socket: socket.socket | None
    _ip: str
    _port: int
    _timeout: int
    
    def __init__(self, ip: str, port: int = 60101, timeout: int | None = None):
        self._socket = None
        self._ip = ip
        self._port = port
        self._timeout = timeout
    
    @staticmethod
    def process_read_command[**P, T, C: Command](command: int) \
            -> Callable[[Callable[P, T]], Callable[Concatenate[C, P], T]]:
        def decorator(func: Callable[P, T]) -> Callable[Concatenate[C, P], T]:
            @functools.wraps(func)
            def wrapper(self: C, *args: P.args, **kwargs: P.kwargs) -> T:
                response = self.exec_command(command.to_bytes(1))
                if response[0] != command:
                    raise InvalidResponseError(f'received: {hex(response[0])}, expected: {hex(command)}, '
                                               + f'response: {response}')
                return func(self, response[1:], *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def check_response_status[**P, T, C: Command](raise_error: bool = False) \
            -> Callable[[Callable[P, T]], Callable[Concatenate[C, bytes, P], T]]:
        def decorator(func: Callable[P, T]) -> Callable[Concatenate[C, bytes, P], T]:
            @functools.wraps(func)
            def wrapper(self: C, response: bytes, *args: P.args, **kwargs: P.kwargs) -> T:
                if response[0] != 0x00:  # maybe - 0x00: success, 0x01: failed
                    if raise_error:
                        raise FailureMessageReceivedError(f'received: {hex(response[0])}, expected: 0x00, '
                                                          + f'response: {response}')
                if '_status' in inspect.signature(func).parameters:
                    return func(self, response[1:], *args, **kwargs, _status=response[0])
                return func(self, response[1:], *args, **kwargs)
            return wrapper
        return decorator
    
    # crc8 reference: https://blog.goo.ne.jp/masaki_goo_2006/e/69f286d90e6140e6e8c021e43a11c815
    @staticmethod
    def crc8(data: bytes, poly: int = 0x85, init: int = 0x00) -> int:
        result = init
        for byte in data:
            result ^= byte
            for _ in range(8):
                if result & 0x80:
                    result = (result << 1) ^ poly
                else:
                    result <<= 1
        return result & 0xff
    
    @classmethod
    def get_command_binary(cls, command: bytes) -> bytes:
        return b'\xaa' + len(command).to_bytes(2, 'big') + command + cls.crc8(command).to_bytes(1)
    
    def exec_command(self, data: bytes) -> bytes:
        if self._socket is not None:
            self._socket.close()
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect((self._ip, self._port))
        self._socket.sendall(self.get_command_binary(data))
        data = self.receive_message()
        self._socket.close()
        self._socket = None
        return data
    
    def receive_message(self) -> bytes:
        if self._socket is None:
            raise SocketNotAvailableError
        
        header = self.receive_bytes(1)
        if header != b'\xaa':
            raise UnexpectedDataReceivedError
        
        length_expected = int.from_bytes(self.receive_bytes(2), 'big')
        data = self.receive_bytes(length_expected)
        length_received = len(data)
        if length_received != length_expected:
            raise DataDroppedError(f'received: {length_received} bytes, expected: {length_expected} bytes, '
                                   + f'data: {data}')
        
        crc_received = int.from_bytes(self.receive_bytes(1))
        crc_calculated = self.crc8(data)
        if crc_received != crc_calculated:
            raise InvalidCrcError(f'received: {crc_received}, calculated: {crc_calculated}, '
                                  + f'data: {data}')
        
        return data
    
    def receive_bytes(self, length: int, wait: int | None = None) -> bytes:
        if self._socket is None:
            raise SocketNotAvailableError
        if wait is None:
            wait = self._timeout
        wait_count = 0
        data = bytearray()
        while len(data) < length:
            received = self._socket.recv(length - len(data))
            if not received:
                if wait_count < wait:
                    wait_count += 1
                    time.sleep(1)
                    continue
                else:
                    break
            data.extend(received)
        return bytes(data)
    
    @process_read_command(0xa2)
    @check_response_status(False)
    def get_name(self, _response: bytes, _status: int) -> str:
        if _status != 0x00:
            return ''
        length_expected = _response[0]
        name = _response[1:]
        length_received = len(name)
        if length_received != length_expected:
            raise DataDroppedError(f'received: {length_received} bytes, expected: {length_expected} bytes, '
                                   + f'response: {_response}')
        return name.decode('utf-8')
    
    def set_name(self, name: str) -> None:
        name_bin = name.encode('utf-8')
        response = self.exec_command(b'\xa1' + len(name_bin).to_bytes(1) + name_bin)
        if response != b'\xa1\x00':
            raise SetNameFailedError(f'response: {response}')
        return
        
    @process_read_command(0xc4)
    @check_response_status(True)
    def get_version(self, _response: bytes) -> str:
        length_expected = int.from_bytes(_response[0:2])
        version = _response[2:]
        length_received = len(version)
        if length_received != length_expected:
            raise DataDroppedError(f'received: {length_received} bytes, expected: {length_expected} bytes, '
                                   + f'response: {_response}')
        
        return version.decode('utf-8')
    
    @staticmethod
    def parse_voltage(raw_data: bytes) -> float:
        return float(int.from_bytes(raw_data, 'little') / (1 << 24))
    
    @staticmethod
    def parse_current(raw_data: bytes) -> float:
        return float(int.from_bytes(raw_data, 'little') / (1 << 30))
    
    @staticmethod
    def parse_power(raw_data: bytes) -> float:
        return float(int.from_bytes(raw_data, 'little') / (1 << 24))
    
    @staticmethod
    def parse_timestamp(raw_data: bytes) -> datetime:
        return datetime(raw_data[5] + 1900, raw_data[4] + 1, raw_data[3], raw_data[2], raw_data[1], raw_data[0])
    
    @process_read_command(0x18)
    @check_response_status(False)
    def get_measurement(self, _response: bytes, _status: int) -> dict[str, float | datetime]:
        if _status != 0x00:  # maybe - 0x00: success, 0x01: failed
            raise GetMeasurementFailedError(f'status: {hex(_status)}, response: {_response}')
        
        return {
            'voltage': self.parse_voltage(_response[0:6]),
            'current': self.parse_current(_response[6:12]),
            'power': self.parse_power(_response[12:18]),
            'timestamp': self.parse_timestamp(_response[18:24]),
        }
    
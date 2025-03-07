import datetime

from .error import *
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.exceptions import InfluxDBError


class Influx2:
    _client: InfluxDBClient | None = None
    _org: str
    _bucket: str
    
    def __init__(self, url: str, org: str, token: str, bucket: str):
        try:
            self._client = InfluxDBClient(url=url, org=org, token=token)
        except InfluxDBError as e:
            if self._client is not None:
                self._client.close()
            raise DbConnectError from e
        self._org = org
        self._bucket = bucket
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
        
    def save_watt_data(self, measurement: str, voltage: float, current: float, power: float, sensor: str | None = '',
                       ip: str | None = '', timestamp: datetime.datetime | None = None) -> None:
        if self._client is None:
            raise DbNotAvailableError
        if sensor is None:
            sensor = ''
        if ip is None:
            ip = ''
        with self._client.write_api() as _write_client:
            point = Point(measurement).tag('sensor', sensor).tag('ip', ip)
            point = point.field('voltage', float(voltage)).field('current', float(current)).field('power', float(power))
            if timestamp is not None:
                point = point.time(timestamp)
            _write_client.write(self._bucket, self._org, point)
        
import os
import sys
import tomllib
import datetime

import datastorelib
import wattchecklib


def main():
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(location, 'settings.toml'), 'rb') as f:
        settings = tomllib.load(f)
        
    datastore = settings['wattcheck']['datastore']
    if settings[datastore]['type'] != 'influx2':
        raise NotImplementedError
    
    save_data_list = []
    for sensor in settings['sensors']:
        match sensor['type']:
            case 'RS-WFWATTCH1':
                wattcheck_client = wattchecklib.Command(sensor['ip'], sensor['port'])
            case 'RS-WFWATTCH2':
                wattcheck_client = wattchecklib.Command2(sensor['ip'], sensor['port'])
            case _:
                raise NotImplementedError
        sensor_name = wattcheck_client.get_name()
        measured_data = wattcheck_client.get_measurement()
        save_data = [
            measured_data['voltage'], measured_data['current'], measured_data['power'], sensor_name, sensor['ip']
        ]
        if settings['wattcheck']['use_sensor_timestamp']:
            timezone = datetime.timezone(datetime.timedelta(hours=settings['wattcheck']['sensor_timezone']))
            timestamp_with_timezone = measured_data['timestamp'].replace(tzinfo=timezone)
            save_data.append(timestamp_with_timezone)
        save_data_list.append(save_data)
        
    with datastorelib.Influx2(settings[datastore]['url'], settings[datastore]['org'], settings[datastore]['token'],
                              settings[datastore]['bucket']) as datastore_client:
        for save_data in save_data_list:
            # print(save_data)
            datastore_client.save_watt_data(settings[datastore]['measurement'], *save_data)


if __name__ == '__main__':
    sys.exit(main())

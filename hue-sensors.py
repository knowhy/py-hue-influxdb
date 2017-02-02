#/usr/bin/env python3
#
# hue-sensors.py
#
# store HUE sensors data in influxdb
#
# author: Henrik Pingel
# email: knowhy@gmail.com
#
# license: MIT

import json
import requests
import time
from influxdb import InfluxDBClient
from datetime import datetime

influxdb_dbname = 'test'
influxdb_user = 'admin'
influxdb_password = 'admin'
influxdb_host = 'influxdb host'
influxdb_port = 'influxdb port'
hue_host = "hue bridge ip"
hue_user = "hue bridge user api key"
update_interval = 1

client = InfluxDBClient(influxdb_host, influxdb_port, influxdb_user, influxdb_password, influxdb_dbname)

def update_data():
    r = requests.get(url="http://" + hue_host + "/api/" + hue_user + "/sensors")
    j = r.json()
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    for key in j.items():
        
        if key[1]['type'] == 'ZLLLightLevel':
            json_body = [
                {
                    "measurement": "lightlevel",
                    "tags": {
                        "sensor": key[1]['name']
                    },
                    "time": current_time,
                    "fields": {
                        "value": key[1]['state']['lightlevel'],
                    }
                }
            ]
            client.write_points(json_body)

        if key[1]['type'] == 'ZLLTemperature':
            value_string = str(key[1]['state']['temperature'])
            json_body = [
                {
                    "measurement": "temperature",
                    "tags": {
                        "sensor": key[1]['name']
                },
                    "time": current_time,
                    "fields": {
                         "value": value_string[:2] + '.' + value_string[-2:]
                    }
                }
            ]
            client.write_points(json_body)

        if key[1]['type'] == 'ZLLPresence':
            presence_state = key[1]['state']['presence']
            if presence_state == False:
                presence_value = 0
            else:
                presence_value = 1

            json_body = [
                {
                    "measurement": "status",
                    "tags": {
                        "sensor": key[1]['name']
                },
                    "time": current_time,
                    "fields": {
                        "value": presence_value
                    }
                }
            ]
            client.write_points(json_body)

    time.sleep(update_interval)
    
while True:
    update_data()

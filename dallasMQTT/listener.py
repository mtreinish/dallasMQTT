# Copyright 2016 Matthew Treinish
#
# This file is part of dallasMQTT
#
# dallasMQTT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dallasMQTT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dallasMQTT.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import threading
import time

import paho.mqtt.publish as publish
from six import moves
import yaml


class DallasTemp(threading.Thread):

    def __init__(self, sensors, queue, pollrate=2):
        super(DallasTemp, self).__init__()
        self.sensors = sensors
        self.pollrate = pollrate
        self.queue = queue

    def _read(self, path):
        with open(path, 'r') as sensor_out:
            split_out = sensor_out.read().split('\n')
            status = split_out[0]
            if status.endswith('YES'):
                raw_out = split_out[1]
                temp_data = raw_out.split('=')[1]
                resp = float(temp_data) / 1000.0
            else:
                resp = None
        return resp

    def run(self):
        while True:
            for sensor in self.sensors:
                sensor_id = sensor['id']
                path = os.path.join('/sys/bus/w1/devices', sensor['id'],
                                    'w1_slave')
                resp = self._read(path)
                if resp:
                    out_dict = {
                        'sensor_id': sensor_id,
                        'temperature': resp,
                    }
                    self.queue.put(out_dict)
            time.sleep(self.pollrate)


class PushMQTT(object):
    def __init__(self, hostname, port=1883, client_id=None,
                 keepalive=60, will=None, auth=None, tls=None):
        self.hostname = hostname
        self.port = port
        self.client_id = client_id
        self.keepalive = 60
        self.will = will
        self.auth = auth
        self.tls = tls

    def publish_single(self, topic, msg):
        publish.single(topic, msg, hostname=self.hostname,
                       port=self.port, client_id=self.client_id,
                       keepalive=self.keepalive, will=self.will,
                       auth=self.auth, tls=self.tls)


def _parse_config(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file.read())
    return config


def create_mqtt(config):
    auth = None
    if 'username' in config:
        auth = {'username': config['username']}
        if 'password' in config:
            auth['password'] = config['password']

    return PushMQTT(config['mqtt']['hostname'], auth=auth)


def partition_sensors(sensors, maxthreads):
    if len(sensors) <= maxthreads:
        return [[x] for x in sensors]
    output = []
    for i in range(0, len(sensors), maxthreads):
        end = i + maxthreads
        output.append(sensors[i:end])
    return output


def main():
    config = _parse_config(sys.argv[1])
    sensor_ids = config['sensors']

    base_topic = 'dallasMQTT'
    if 'default' in config and 'base_topic' in config['default']:
        base_topic = config['default']['base_topic']

    pollrate = 2
    if 'default' in config and 'poll_rate' in config['default']:
        pollrate = config['default']['poll_rate']

    maxthreads = 2
    if 'default' in config and 'max_threads' in config['default']:
        maxthreads = config['default']['max_threads']

    temperature_queue = moves.queue.Queue()
    mqtt = create_mqtt(config)
    for sensors in partition_sensors(sensor_ids, maxthreads):
        temp_sensor = DallasTemp(sensors, temperature_queue, pollrate)
        temp_sensor.start()

    while True:
        temp = temperature_queue.get()
        sensor_name = [x['name'] for x in sensor_ids if
                       x['id'] == temp['sensor_id']][0]
        topic = base_topic + '/' + sensor_name
        mqtt.publish_single(topic, temp['temperature'])

if __name__ == "__main__":
    main()

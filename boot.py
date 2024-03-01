# boot.py -- run on boot-up
# Add time sync

import time
import ubinascii
from machine import Pin, unique_id, SoftI2C
import micropython
import network
import esp
import gc
import scrt
import ntptime
import dht 
from umqtt.robust import MQTTClient
from hamqtt import Sensor, BinarySensor
import ujson as json
from bh1750 import BH1750

# TODO: Initiate sensors
DHT_PIN = 5
SCL_PIN = Pin(22)
SDA_PIN = Pin(21)
i2c = SoftI2C(scl = SCL_PIN, sda = SDA_PIN)
PIR_PIN = Pin(23, Pin.IN)

dht_sensor = dht.DHT22(Pin(DHT_PIN))
light_sensor = BH1750(i2c)

device_id = scrt.DEVNAME + '_' + ubinascii.hexlify(unique_id()).decode()
device_name = scrt.DEVHUMNAME + ' (' + ubinascii.hexlify(unique_id()).decode() + ')'

def timestr():
    t = time.localtime()
    return ('{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}'.format(t[2], t[1], t[0], t[3], t[4], t[5]))

def log(str):
    str = timestr() + ' ' + str
    print(str)
    # TODO do log

def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(scrt.SSID, scrt.WIFIPWD)
    while station.isconnected() == False:
        print('\r' + str(time.localtime()[5]), end='')
    pass
    print('')
    log('Connection successful')
    print(station.ifconfig())
    ntptime.settime()
    log('NTP time syncronized. UTC time: ' + timestr())

def mqtt_connect_discovery():
    global device_id, mqtt_sensor_temperature, mqtt_sensor_humidity, mqtt_sensor_light, mqtt_sensor_motion
    mqtt_client = MQTTClient(device_id, scrt.MQTTSERVER, 0, scrt.MQTTUSER, scrt.MQTTPWD, keepalive = scrt.UPDPERIOD + 10)
    mqtt_client.connect()
    log('Connected to {}:{} MQTT broker'.format(mqtt_client.server, mqtt_client.port))

    sensor_id = device_id + '_temperature'
    identifiers = { "identifiers":[sensor_id] }
    sensor_temperature_config = { "unit_of_measurement": "°C", "device_class": "temperature", "value_template": "{{ value_json.temperature }}", "devices":identifiers }
    mqtt_sensor_temperature = Sensor(mqtt_client, device_name.encode('utf-8'), sensor_id.encode('utf-8'), extra_conf=sensor_temperature_config)
    
    sensor_id = device_id + '_humidity'
    identifiers = { "identifiers":[sensor_id] }
    sensor_humidity_config = { "unit_of_measurement": "%", "device_class": "humidity", "value_template": "{{ value_json.humidity }}", "devices":identifiers }
    mqtt_sensor_humidity = Sensor(mqtt_client, device_name.encode('utf-8'), sensor_id.encode('utf-8'), extra_conf=sensor_humidity_config)

    sensor_id = device_id + '_light'
    identifiers = { "identifiers":[sensor_id] }
    sensor_light_config = { "unit_of_measurement": "lx", "device_class": "illuminance", "value_template": "{{ value_json.value }}", "devices":identifiers }
    mqtt_sensor_light = Sensor(mqtt_client, device_name.encode('utf-8'), sensor_id.encode('utf-8'), extra_conf=sensor_light_config)

    sensor_id = device_id + '_motion'
    identifiers = { "identifiers":[sensor_id] }
    sensor_motion_config = { "device_class": "motion", "value_template": "{{ value_json.value }}", "devices":identifiers }
    mqtt_sensor_motion = BinarySensor(mqtt_client, device_name.encode('utf-8'), sensor_id.encode('utf-8'), extra_conf=sensor_motion_config)

    return mqtt_client


connect_wifi()

mqtt_client = mqtt_connect_discovery() # should it be in the main loop?
mqtt_client.DEBUG = True

esp.osdebug(None)
gc.collect()





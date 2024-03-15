# boot.py -- run on boot-up
# Add time sync

import time
import ubinascii
from machine import Pin, unique_id, SoftI2C, deepsleep, wake_reason, PIN_WAKE
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
import esp32

DHT_PIN = 5
SCL_PIN = Pin(22)
SDA_PIN = Pin(21)
i2c = SoftI2C(scl = SCL_PIN, sda = SDA_PIN)
PIR_PIN = Pin(15, Pin.IN)

station = None              #WiFi client        

dht_sensor = dht.DHT22(Pin(DHT_PIN))
light_sensor = BH1750(i2c)

esp32.wake_on_ext0(pin = PIR_PIN, level = esp32.WAKEUP_ANY_HIGH)

device_id = scrt.DEVNAME + '_' + ubinascii.hexlify(unique_id()).decode()
device_name = scrt.DEVHUMNAME + ' (' + ubinascii.hexlify(unique_id()).decode() + ')'

saved_data = { 'motion' : False, 'temperature' : -255, 'humidity' : -255, 'light' : -255 }

def timestr():
    t = time.localtime()
    return ('{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}'.format(t[2], t[1], t[0], t[3], t[4], t[5]))

def log(str):
    str = timestr() + ' ' + str
    print(str)
    # TODO do log

log('Woke up with reson {}'.format(wake_reason()))

def load_json(json_file):
    try:
        with open(json_file) as f:
            d = json.loads(f.read())
            f.close()
            return d
    except OSError as e:
        log('Failed to load JSON file {}. Error {}'.format(json_file, e))
        return None

def save_json(json_file, data):
    try:
        with open(json_file, 'w') as f:
            f.write(json.dumps(data))
            f.close()
            return True
    except OSError as e:
        log('Failed to load JSON file {}. Error {}'.format(json_file, e))
        return False

def deep_sleep():
    global station
    if station:
        station.disconnect()
    log('Going deep sleep for {} sec'.format(scrt.UPDPERIOD))
    deepsleep(scrt.UPDPERIOD * 1000)

json_data = load_json(scrt.DATAFILE)
if isinstance(json_data, dict):
    saved_data = json_data
    log('Loaded saved data from file: {}'.format(saved_data))

if wake_reason() == PIN_WAKE:   # if ESP woke up by PIR
    if saved_data['motion']:    # if saved last motion status is active then do nothing, go deep sleep
        time.sleep(5)
        deep_sleep()
    else:                       # if motion was not active toggle it and set PIR triggered
        saved_data['motion'] = True
else:
    if saved_data['motion']:
        saved_data['motion'] = False

def connect_wifi():
    global station
    try:
        station = network.WLAN(network.STA_IF)
        station.active(True)
        start = time.time()
        station.connect(scrt.SSID, scrt.WIFIPWD)
        while station.isconnected() == False:
            print('\r' + timestr(), end='')
            if time.time() - start > scrt.WIFITIMOUT:
                raise OSError(ETIMEDOUT)
            time.sleep_ms(200)
        print('')
        log('Connection successful')
        print(station.ifconfig())
        return True
    except OSError as e:
        log('Failed to connect WIFI. Error {}'.format(e))
        return False
    
def sync_time():
    try:
        ntptime.settime()
        log('NTP time syncronized. UTC time: ' + timestr())
    except OSError as e:
        log('Failed to synchronize time. Error {}'.format(e))
        return False

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

    return mqtt_client;


if connect_wifi():
    sync_time()
    try:
        mqtt_client = mqtt_connect_discovery() 
        mqtt_client.DEBUG = True
    except OSError as e:
        log('Failed to connect to MQTT broker. Error {}'.format(e))
        deep_sleep()
else:
    deep_sleep()

esp.osdebug(None)
gc.collect()





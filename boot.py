# boot.py -- run on boot-up
# Add time sync

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import gc
import scrt

esp.osdebug(None)
gc.collect()

device_id = ubinascii.hexlify(machine.unique_id()).decode()

def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(scrt.SSID, scrt.WIFIPWD)
    while station.isconnected() == False:
        print('\r' + str(time.localtime()[5]), end='')
    pass
    print('')
    print('Connection successful')
    print(station.ifconfig())

def connect_mqtt():
    global device_id
    client = MQTTClient(device_id, scrt.MQTTSERVER, 0, scrt.MQTTUSER, scrt.MQTTPWD)
    client.connect()
    print('Connected to {} MQTT broker'.format(mqtt_server))
    return client

connect_wifi()
client = connect_mqtt()

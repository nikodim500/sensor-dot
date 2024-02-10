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
import ntptime

esp.osdebug(None)
gc.collect()

# TODO: Initiate pins

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
    ntptime.settime()
    t = time.localtime()
    print('NTP time syncronized. UTC time: {}/{}/{} {}:{}:{}'.format(t[2], t[1], t[0], t[3], t[4], t[5]))

def connect_mqtt():
    global device_id
    client = MQTTClient(device_id, scrt.MQTTSERVER, 0, scrt.MQTTUSER, scrt.MQTTPWD)
    client.connect()
    print('Connected to {}:{} MQTT broker'.format(client.server, client.port))
    return client
# TODO: MQTT Home Assistant discovery

connect_wifi()
client = connect_mqtt()

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

ssid = scrt.SSID
wifi_password = scrt.WIFIPWD
mqtt_server = scrt.MQTTSERVER
mqtt_user = scrt.MQTTUSER
mqtt_password = scrt.MQTTPWD
client_id = ubinascii.hexlify(machine.unique_id()).decode()

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, wifi_password)

while station.isconnected() == False:
  print('/r' + time.localtime()[5], end='')
  pass

print('Connection successful')
print(station.ifconfig())
# main.py 

import machine
from time import sleep
import dht 

sensor = dht.DHT22(machine.Pin(5))
#sensor = dht.DHT11(machine.Pin(5))

def deep_sleep(msecs):
  #configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
  # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
  rtc.alarm(rtc.ALARM0, msecs)
  #put the device to sleep
  machine.deepsleep()

temperature = -273
humidity = -100

def send_measures():
  print('Temperature: {} C'.format(temperature))
  print('Humidity: {} %'.format(humidity))
  # TODO: Print light measures 
  # TODO: MQTT broadcast
  

  # TODO: PIR detection

while True:
  try:
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temperature = temp
    humidity = hum
    # TODO: Light measures
    send_measures()
    # TODO: Deep sleep
    # deep_sleep(300000)

    # TODO: Treshold for WiFi/MQTT reconnection
  except OSError as e:
    print('Failed to read sensor.')
  sleep(2)

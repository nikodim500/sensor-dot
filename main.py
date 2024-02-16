# main.py 
# Imports and initiations in boot.py

def deep_sleep(msecs):
  #configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
  # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
  rtc.alarm(rtc.ALARM0, msecs)
  #put the device to sleep
  machine.deepsleep()

temperature = -255
humidity = -255
light = -255

def send_measures():
  print('Temperature: {} C'.format(temperature))
  print('Humidity: {} %'.format(humidity))
  print('Light level: {} lux'.format(light))
  # TODO: Print light measures 
  # TODO: MQTT broadcast
  payload = json.dumps({"temperature":temperature})
  mqtt_sensor_temperature.publish_state(payload)
  payload = json.dumps({"humidity":humidity})
  mqtt_sensor_humidity.publish_state(payload)

# TODO: PIR detection

while True:
  try:
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    # TODO: Treshold for WiFi/MQTT reconnection
  except OSError as e:
    print('Failed to read DHT sensor.{}'.format(e))

  try:
    light = light_sensor.luminance(BH1750.ONCE_HIRES_1)
  except OSError as e:
    print('Failed to read light sensor.{}'.format(e))
    # TODO: More meaningful error handling

  send_measures()
  time.sleep(5)
#  time.sleep(scrt.UPDPERIOD)

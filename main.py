# main.py 
# Imports and initiations in boot.py

def deep_sleep(secs):
  log('Going deep sleep for {} sec'.format(secs))
  machine.deepsleep(secs * 1000)

temperature = -255
humidity = -255
light = -255
motion = False
PIR_triggered = False

def send_measures():
  global temperature, humidity, light, motion, PIR_triggered
  log('Temperature: {} C'.format(temperature))
  log('Humidity: {} %'.format(humidity))
  log('Light level: {} lux'.format(light))
  # TODO: Print light measures 
  # TODO: MQTT broadcast
  payload = json.dumps({"temperature":temperature})
  mqtt_sensor_temperature.publish_state(payload)
  payload = json.dumps({"humidity":humidity})
  mqtt_sensor_humidity.publish_state(payload)
  payload = json.dumps({"value":light})
  mqtt_sensor_light.publish_state(payload)

def do_measure():
  try:
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    # TODO: Treshold for WiFi/MQTT reconnection
  except OSError as e:
    log('Failed to read DHT sensor.{}'.format(e))

  try:
    light = round(light_sensor.luminance(BH1750.ONCE_HIRES_2), 1)
  except OSError as e:
    log('Failed to read light sensor.{}'.format(e))

while True:
  send_measures()
  do_measure()
  deep_sleep(scrt.UPDPERIOD)
#  time.sleep(scrt.UPDPERIOD)

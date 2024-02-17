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
motion = False
PIR_triggered = False

def do_interrupt(Pin):
  global motion, PIR_triggered
  if Pin.value() == 1:
    print(timestr() + ' Motion detected ON')
    motion = True
  else:
    print(timestr() + ' Motion detected OFF')
    motion = False
  PIR_triggered = True

PIR_PIN.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=do_interrupt)

def send_measures():
  global temperature, humidity, light, motion, PIR_triggered
  print(timestr() + ' Temperature: {} C'.format(temperature))
  print(timestr() + ' Humidity: {} %'.format(humidity))
  print(timestr() + ' Light level: {} lux'.format(light))
  # TODO: Print light measures 
  # TODO: MQTT broadcast
  payload = json.dumps({"temperature":temperature})
  mqtt_sensor_temperature.publish_state(payload)
  payload = json.dumps({"humidity":humidity})
  mqtt_sensor_humidity.publish_state(payload)
  payload = json.dumps({"value":light})
  mqtt_sensor_light.publish_state(payload)

  if PIR_triggered:
    PIR_triggered = False
    if motion:
      payload = json.dumps({"value":"on"})
      mqtt_sensor_motion.publish_state(payload)
    else:
      payload = json.dumps({"value":"off"})
      mqtt_sensor_motion.publish_state(payload)

while True:
  try:
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    # TODO: Treshold for WiFi/MQTT reconnection
  except OSError as e:
    print('Failed to read DHT sensor.{}'.format(e))

  try:
    light = round(light_sensor.luminance(BH1750.ONCE_HIRES_2), 1)
  except OSError as e:
    print('Failed to read light sensor.{}'.format(e))
    # TODO: More meaningful error handling

  send_measures()
  time.sleep(5)
#  time.sleep(scrt.UPDPERIOD)

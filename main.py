# main.py 
# Imports and initiations in boot.py

def discovery_message(device_name_suffix, controllable = 0): # Make discovery message for Home Assistant
  global device_id
  payload={"unique_id": "{}".format(device_id),
      "name": "{}".format(device_name),
      "state_topic": "homeassistant/sensor/{}".format(device_id),
      "command_topic": "homeassistant/sensor/{}/set".format(device_id),
      "availability_topic":"homeassistant/sensor/{}/available".format(device_id),
      "payload_on": "ON",
      "payload_off": "OFF",
      "state_on": "ON",
      "state_off": "OFF",
      "optimistic": False,
      "qos": 0,
      "retain": True
  }
  payload=json.dumps(payload) #convert to JSON
  return payload

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
    # TODO: Light measures
    send_measures()
    # TODO: Deep sleep
    # deep_sleep(300000)

    # TODO: Treshold for WiFi/MQTT reconnection
  except OSError as e:
    print('Failed to read sensor.')
    # TODO: More meaningful error handling
  time.sleep(scrt.UPDPERIOD)

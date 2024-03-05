# main.py 
# Imports and initiations in boot.py

def send_measures():
    global PIR_triggered, mqtt_sensor_motion
    log('Temperature: {} C'.format(saved_data['temperature']))
    log('Humidity: {} %'.format(saved_data['humidity']))
    log('Light level: {} lux'.format(saved_data['light']))
    payload = json.dumps({"temperature":saved_data['temperature']})
    mqtt_sensor_temperature.publish_state(payload)
    payload = json.dumps({"humidity":saved_data['humidity']})
    mqtt_sensor_humidity.publish_state(payload)
    payload = json.dumps({"value":saved_data['light']})
    mqtt_sensor_light.publish_state(payload)
    if PIR_triggered:
        PIR_triggered = False
        if saved_data['motion']:
            log('Motion ON')
            mqtt_sensor_motion.on
        else:
            mqtt_sensor_motion.off
            log('Motion OFF')
    else:
        log('Motion activity: {}'.format(saved_data['motion'])) 


def do_measure():
    global saved_data
    try:
        dht_sensor.measure()
        saved_data['temperature'] = dht_sensor.temperature()
        saved_data['humidity'] = dht_sensor.humidity()
        # TODO: Treshold for WiFi/MQTT reconnection
    except OSError as e:
        log('Failed to read DHT sensor.{}'.format(e))
    try:
        saved_data['light'] = round(light_sensor.luminance(BH1750.ONCE_HIRES_2), 1)
    except OSError as e:
        log('Failed to read light sensor.{}'.format(e))
    save_json(scrt.DATAFILE, saved_data)

while True:
    do_measure()
    send_measures()
    deep_sleep()
  #  time.sleep(scrt.UPDPERIOD)

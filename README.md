**Sensor-dot** is a small self-made device to track temperature, humidity, light intensity and movments.

**Features**

_Implemented_
- WiFi connection
- NTP time syncronization
- MQTT broker connection
- Temperature measurement
- Humidity measurement
  
_TODO_
- Temperature measurement MQTT broadcasting
- Humidity measurement MQTT broadcasting
- Battery power hardware setup
- Deep sleep between measures
- Light intensity measurement
- Light intensity MQTT broadcasting
- PIR movement detection
- PIR movement detection MQTT broadcasting
- ?Wake up on PIR movement detection

_Hardware_

Based on ESP8266/ESP32 platform it integrates with Home Assistant via MQTT.
Power supply is two AA batteries.
Sensors:
Temperature and humidity - DHT22

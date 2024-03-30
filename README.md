# Elsner Sensor

### Installation

Copy this folder to `<config_dir>/custom_components/elsner/`.

Add the following to your `configuration.yaml` file:

```yaml
# configuration.yaml entry
sensor:
  - platform: elsner
    name: weather_station
    serial_port: dev/ttyUSB0

template:
  - sensor:
      - name: Temperature
        unit_of_measurement: "°C"
        state: "{{ iif(states('sensor.weather_station')[1:6] | int >= 0, states('sensor.weather_station')[2:6], states('sensor.weather_station')[1:6]) }}"
        device_class: current
      - name: Sun south
        unit_of_measurement: "kLux"
        state: "{{ states('sensor.weather_station')[6:8] }}"
        device_class: current
      - name: Sun west
        unit_of_measurement: "kLux"
        state: "{{ states('sensor.weather_station')[8:10] }}"
        device_class: current
      - name: Sun east
        unit_of_measurement: "kLux"
        state: "{{ states('sensor.weather_station')[10:12] }}"
        device_class: current
      - name: is dark
        unit_of_measurement: "bool"
        state: >
          {% if 'J' in states('sensor.weather_station'[12]) -%}                
            0
          {% else -%}
            1
          {% endif -%}
        device_class: current
      - name: Daylight
        unit_of_measurement: "Lux"
        state: "{{ states('sensor.weather_station')[13:16] }}"
        device_class: current
      - name: Wind
        unit_of_measurement: "km/h"
        state: "{{ (states('sensor.weather_station')[16:20] | float * 3.6) }}"
        device_class: current
      - name: is raining
        unit_of_measurement: "bool"
        state: >
          {% if 'J' in states('sensor.weather_station'[20]) -%}                
            1
          {% else -%}
            0
          {% endif -%}
```
[sensor.py](sensor.py)

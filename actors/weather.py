
def aggregate_sensor_values_all(data):
    athm_pressure = (data["atmo_pressure_sensor_1"] + data["atmo_pressure_sensor_2"]) / 2.0
    humidity = (data["humidity_sensor_1"] + data["humidity_sensor_2"]) / 2.0
    light = (data["light_sensor_1"] + data["light_sensor_2"]) / 2.0
    temperature = (data["temperature_sensor_1"] + data["temperature_sensor_2"]) / 2.0
    wind_speed = (data["wind_speed_sensor_1"] + data["wind_speed_sensor_2"]) / 2.0
    timestamp = data["unix_timestamp_us"]

    return athm_pressure, humidity, light, temperature, wind_speed, timestamp


def aggregate_sensor_values_iot(data):
    if(isinstance(data, str) ):
        data = eval(data)

    athm_pressure = (data["atmo_pressure_sensor_1"] + data["atmo_pressure_sensor_2"]) / 2.0
    wind_speed = (data["wind_speed_sensor_1"] + data["wind_speed_sensor_2"]) / 2.0
    timestamp = data["unix_timestamp_100us"]

    return  wind_speed, athm_pressure, timestamp


def aggregate_sensor_values_sensors(data):
    if(isinstance(data, str) ):
        data = eval(data)

    light = (data["light_sensor_1"] + data["light_sensor_2"]) / 2.0
    timestamp = data["unix_timestamp_100us"]

    return light, timestamp


def aggregate_sensor_values_legacy_sensors(data):
    if(isinstance(data, str) ):
        data = eval(data)

    humidity = (data["humidity_sensor_1"] + data["humidity_sensor_2"]) / 2.0
    temperature = (data["temperature_sensor_1"] + data["temperature_sensor_2"]) / 2.0
    timestamp = data["unix_timestamp_100us"]

    return humidity, temperature, timestamp




def predict_weather(athm_pressure, humidity, light, temperature, wind_speed):
    if (temperature < -2 and light < 128) and athm_pressure < 720:
        return 'SNOW'
    if temperature < -2 and light > 128 and athm_pressure < 680:
        return "WET_SNOW"
    if temperature < -8:
        return 'SNOW'
    if temperature < -15 and wind_speed > 45:
        return "BLIZZARD"
    if temperature > 0 and athm_pressure < 710 and humidity > 70 and wind_speed < 20:
        return "SLIGHT_RAIN"
    if temperature > 0 and athm_pressure < 690 and humidity > 70 and wind_speed > 20:
        return "HEAVY_RAIN"
    if temperature > 30 and athm_pressure < 770 and humidity > 80 and light > 192:
        return "HOT"
    if temperature > 30 and athm_pressure < 770 and humidity > 50 and light > 192 and wind_speed > 35:
        "CONVECTION_OVEN"
    if temperature > 25 and athm_pressure < 750 and humidity > 70 and light < 192 and wind_speed < 10:
        return "WARM"
    if temperature > 25 and athm_pressure < 750 and humidity > 70 and light < 192 and wind_speed > 10:
        return "SLIGHT_BREEZE"
    if light < 128:
        return "CLOUDY"
    if temperature > 30 and athm_pressure < 660 and humidity > 85 and wind_speed > 45:
        return "MONSOON"

    return "JUST_A_NORMAL_DAY"


def print_aggregated_values(athm_pressure, humidity, light, temperature, wind_speed):
    print("ATHM PRESSURE:", athm_pressure)
    print("HUMIDITY:", humidity)
    print("LIGHT: ", light)
    print("TEMPERATURE:", temperature)
    print("WIND_SPEED: ", wind_speed)
    print("TIMESTAMP: ", timestamp)

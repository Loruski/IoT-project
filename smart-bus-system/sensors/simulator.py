
import time
import os
import paho.mqtt.client as mqtt
from classes import Bus, Stop 
from dotenv import load_dotenv
from configReader import read_buses_config, read_city_params, read_stop_config, reload_buses, reload_stops
import configReader
import random

# Load environment variables
# load_dotenv()
ADMIN_USERNAME = os.getenv("IOT_USERNAME")
ADMIN_PASSWORD = os.getenv("IOT_PASSWORD")

print("Admin username:", ADMIN_USERNAME)
print("Admin password:", ADMIN_PASSWORD)

BROKER_IP = "20.0.0.20"

# Topics
BUS = "bus"
STOP = "stop"

# Sensor types for stops
TEMP = "temp"
RAIN = "rain"
PEOPLE = "people"

# Sensor types for buses
CURRENT_STOP = "current_stop"
CURRENT_CAPACITY = "current_capacity"
STATUS = "status"

# Topic structure:
# For stops: stop/{stop_id}/{sensor_type}/value
#            stop/{stop_id}/{sensor_type}/timestamp
# For buses: bus/{bus_id}/{sensor_type}/value
#            bus/{bus_id}/{sensor_type}/timestamp



 
def dice_roll_next_stop(global_temp, rain_factor):
    base_probability = 0.2
    # Adjust probability based on environmental factors
    # Higher temperature or rain might slow down or speed up the simulation logic
    adjusted_probability = base_probability + (rain_factor * 0.05) + (global_temp * 0.001)
    
    return random.random() < adjusted_probability

def dice_roll_temperature(global_temp, current_temp = -254.0):
    base_probability = 0.2
    # Adjust temperature slightly based on global temperature
    if current_temp == -254:
        current_temp = global_temp
    variation = random.uniform(-0.5, 0.5)
    new_temp = current_temp + variation
    
    # Keep it within a reasonable range of the global temperature
    if abs(new_temp - global_temp) > 5:
        new_temp = global_temp + variation
        
    return round(new_temp, 2)

def dice_roll_rain_at_stop(rain_factor, current_rain = -1.0):
    base_probability = 0.2
    # Adjust probability based on environmental factors
    if current_rain == -1:
        # Initial state: probability of rain based on rain_factor
        return 1.0 if random.random() < (rain_factor * 0.1) else 0.0
    
    # Transition probability: if it's already raining, it's likely to continue
    # If it's not raining, the chance to start depends on rain_factor
    if current_rain > 0:
        # 80% chance to keep raining, slightly modified by global factors
        stay_rainy = 0.8 + (rain_factor * 0.01)
        return round(max(0, current_rain + random.uniform(-0.1, 0.1)), 2) if random.random() < stay_rainy else 0.0
    else:
        # Chance to start raining
        start_rainy = 0.05 + (rain_factor * 0.02)
        return 0.1 if random.random() < start_rainy else 0.0


def dice_roll_people_at_stop(rain_factor, global_temp, current_people=-1):
    """
    Uses a normal distribution for more realistic population fluctuations.
    """
    if current_people == -1:
        # Initial state: Normal distribution centered at 10
        return max(0, int(random.gauss(10, 5)))
    
    # Base change using a normal distribution (mean 0, std_dev 2)
    # This makes small changes more likely than large jumps
    change = random.gauss(0, 2)
    
    # Environmental impact: shift the mean of the distribution
    # If it's raining or extreme temperature, the mean shift increases
    if rain_factor > 0.5:
        change += random.uniform(0.5, 2.5)
    if global_temp > 30 or global_temp < 5:
        change += random.uniform(0.5, 1.5)
        
    new_people = int(current_people + change)
    
    # Ensure people count is non-negative and within a reasonable limit
    return max(0, min(new_people, 100))




if __name__ == "__main__":
    mqttc = mqtt.Client(protocol=mqtt.MQTTv5)
    
    mqttc.username_pw_set(username=ADMIN_USERNAME,password=ADMIN_PASSWORD)
    print("MQTT is Connecting...")
    mqttc.connect(BROKER_IP, 1883, 60)
    mqttc.loop_start()

    configReader.initialize_system()

    buses: list[Bus] = read_buses_config()
    stops: list[Stop] = read_stop_config()

    while True:
        params = read_city_params()
        global_temp = params.global_temp
        rain_factor = params.rain_factor

        buses: list[Bus] = reload_buses(buses)
        stops: list[Stop] = reload_stops(stops)

        for stop in stops:
            stop.temp = dice_roll_temperature(global_temp, stop.temp)
            stop.rain = dice_roll_rain_at_stop(rain_factor, stop.rain)
            stop.people = dice_roll_people_at_stop(stop.rain, stop.temp, stop.people)

            # Publish stop data to MQTT
            mqttc.publish(f"{STOP}/{stop.id}/{TEMP}/stop_value", stop.temp)
            mqttc.publish(f"{STOP}/{stop.id}/{TEMP}/stop_timestamp", time.time())

            mqttc.publish(f"{STOP}/{stop.id}/{RAIN}/stop_value", stop.rain)
            mqttc.publish(f"{STOP}/{stop.id}/{RAIN}/stop_timestamp", time.time())

            mqttc.publish(f"{STOP}/{stop.id}/{PEOPLE}/stop_value", stop.people)
            mqttc.publish(f"{STOP}/{stop.id}/{PEOPLE}/timestamp", time.time())
            # --- 

            print(stop.name, ":", stop.temp, stop.rain, stop.people)

        for bus in buses:
            if bus.currentStop == None:
                bus.currentStop = bus.route[0]
            elif dice_roll_next_stop(global_temp, rain_factor):
                if bus.route.index(bus.currentStop) == len(bus.route) - 1:
                    bus.currentStop = bus.route[0]
                else:
                    bus.currentStop = bus.route[bus.route.index(bus.currentStop) + 1]
            
            # Publish bus data to MQTT
            mqttc.publish(f"{BUS}/{bus.id}/{CURRENT_STOP}/bus_value", bus.currentStop.id)
            mqttc.publish(f"{BUS}/{bus.id}/{CURRENT_STOP}/bus_timestamp", time.time())
                        # ---
            print(bus.id, bus.currentStop.name)
        
        time.sleep(1)

    mqttc.loop_stop()
    mqttc.disconnect()

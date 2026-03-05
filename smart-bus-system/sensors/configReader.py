import requests
from classes import Bus, Stop, CityParams

API_BASE_URL = "http://20.0.0.11:5000"

buses = []
stops = []
city_params = None

def load_config():
    """Recupera l'intera configurazione tramite API."""
    response = requests.get(f"{API_BASE_URL}/config")
    response.raise_for_status()
    return response.json()
    
def read_stop_config():
    response = requests.get(f"{API_BASE_URL}/stops")
    response.raise_for_status()
    stops_data = response.json()
    
    stops_config = []
    for stop in stops_data:
        stops_config.append(Stop(stop["id"], stop["lat"], stop["lon"], stop["name"]))
    return stops_config

def read_buses_config():
    response = requests.get(f"{API_BASE_URL}/buses")
    response.raise_for_status()
    buses_data = response.json()
    
    buses_config: list[Bus] = []
    
    for bus in buses_data:
        buses_config.append(Bus(bus["id"], bus["route"], bus["capacity"]))

    for bus in buses_config:
        route = []
        route_ids = bus.route
        for stop_id in route_ids:
            for stop in stops:
                if stop.id == stop_id:
                    route.append(stop)
                    break
        bus.route = route
        
    return buses_config

def reload_stops(current_stops: list[Stop]):
    current_stops_dict = {stop.id: stop for stop in current_stops}
    returned_stops = []
    
    for config_stop in read_stop_config():
        if config_stop.id in current_stops_dict:
            existing_stop = current_stops_dict[config_stop.id]
            existing_stop.name = config_stop.name
            existing_stop.lat = config_stop.lat
            existing_stop.lon = config_stop.lon
            returned_stops.append(existing_stop)
        else:
            returned_stops.append(config_stop)
            
    return returned_stops

def reload_buses(current_buses: list[Bus]):
    current_buses_dict = {bus.id: bus for bus in current_buses}
    returned_buses = []
    
    for config_bus in read_buses_config():
        if config_bus.id in current_buses_dict:
            existing_bus = current_buses_dict[config_bus.id]
            existing_bus.route = config_bus.route
            existing_bus.capacity = config_bus.capacity
            returned_buses.append(existing_bus)
        else:
            returned_buses.append(config_bus)
            
    return returned_buses

def modify_city_params(rain_factor, global_temp):
    """
    Invia i nuovi parametri all'API invece di scriverli su file locale.
    """
    payload = {
        "rain_factor": rain_factor,
        "global_temp": global_temp
    }
    response = requests.post(f"{API_BASE_URL}/city_params", json=payload)
    response.raise_for_status()

def read_city_params():
    config = load_config()
    data = config.get("city_params", {})
    return CityParams(data.get("rain_factor"), data.get("global_temp"))

def initialize_system():
    global stops, buses, city_params
    stops = read_stop_config()
    buses = read_buses_config()
    city_params = read_city_params()

if __name__ == "__main__":
    initialize_system()
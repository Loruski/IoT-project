from ast import List
import json

from collections import namedtuple
from classes import Bus, Stop, CityParams

buses = []
stops = []
city_params = None

def load_config():
    with open('/config.json', 'r') as f:
        return json.load(f)

    
def read_stop_config():
    stops_config = []
    config = load_config()
    for stop in config["stops"]:
        stops_config.append(Stop(stop["id"], stop["lat"], stop["lon"],  stop["name"]))
    return stops_config


def read_buses_config():
    config = load_config()
    buses_config: list[Bus] = []
    

    

    for bus in config["buses"]:
        buses_config.append(Bus(bus["id"], bus["route"],  bus["capacity"]))

    for bus in buses_config:
        route = []
        route_ids = bus.route
        for id in route_ids:
            for stop in stops:
                if stop.id == id:
                    route.append(stop)
                    break
        bus.route = route
        
   
    return buses_config


def reload_stops(current_stops: list[Stop]):
    # 1. Creiamo un dizionario degli stop attuali per una ricerca istantanea
    current_stops_dict = {stop.id: stop for stop in current_stops}
    returned_stops = []
    
    # 2. Iteriamo sui dati del JSON, che fungono da "fonte di verità"
    for config_stop in read_stop_config():
        if config_stop.id in current_stops_dict:
            # Lo stop esiste già: aggiorniamo i parametri statici
            existing_stop = current_stops_dict[config_stop.id]
            existing_stop.name = config_stop.name
            existing_stop.lat = config_stop.lat
            existing_stop.lon = config_stop.lon
            
            returned_stops.append(existing_stop)
        else:
            # È un nuovo stop trovato nel JSON, lo aggiungiamo
            returned_stops.append(config_stop)
            
    return returned_stops

def reload_buses(current_buses: list[Bus]):
    # 1. Creiamo un dizionario dei bus attuali
    current_buses_dict = {bus.id: bus for bus in current_buses}
    returned_buses = []
    
    # 2. Iteriamo sui bus letti dal JSON
    for config_bus in read_buses_config():
        if config_bus.id in current_buses_dict:
            # Il bus esiste già: aggiorniamo rotta e capacità
            existing_bus = current_buses_dict[config_bus.id]
            existing_bus.route = config_bus.route
            existing_bus.capacity = config_bus.capacity
            
            returned_buses.append(existing_bus)
        else:
            # È un nuovo bus trovato nel JSON
            returned_buses.append(config_bus)
            
    return returned_buses


def modify_city_params(rain_factor, global_temp):
    # Carica l'intero JSON in memoria 
    config = load_config()

    config["city_params"]["rain_factor"] = rain_factor
    config["city_params"]["global_temp"] = global_temp
    
    # Sovrascrive il file salvando cose modificate
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)


def read_city_params():
    config = load_config()
    data = config["city_params"]
    return CityParams(data["rain_factor"], data["global_temp"])

def initialize_system():
    global stops, buses, cityParams
    stops = read_stop_config()
    buses = read_buses_config()
    cityParams = read_city_params()



if __name__ == "__main__":
    initialize_system()
    

# le funzioni leggono i json e restituiscono gli oggetti di bus e fermata
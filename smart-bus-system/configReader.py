import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)
    
def read_stop_config():
    config = load_config()
    return "ciaoo"


def read_buses_config():
    config = load_config()
    return "ciaoo"


# le funzioni leggono i json e restituiscono gli oggetti di bus e fermata

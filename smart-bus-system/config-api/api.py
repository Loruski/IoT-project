from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
FILE_PATH = 'config.json'

# --- Helper Functions ---
def read_data():
    """Reads the JSON file and returns the data."""
    if not os.path.exists(FILE_PATH):
        # Return a default structure if the file doesn't exist
        return {"city_params": {}, "buses": [], "stops": []}
    with open(FILE_PATH, 'r') as f:
        return json.load(f)

def write_data(data):
    """Writes data back to the JSON file."""
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)

# --- Endpoints for Full Config ---
@app.route('/config', methods=['GET'])
def get_full_config():
    """Returns the entire configuration."""
    return jsonify(read_data()), 200

# --- Endpoints for Buses ---
@app.route('/getBuses', methods=['GET']) # GET the list of buses
def get_buses():
    """Returns the list of buses."""
    data = read_data()
    return jsonify(data.get('buses', [])), 200

@app.route('/addBus', methods=['POST']) # ADD a new bus
def add_bus():
    """Adds a new bus to the configuration."""
    data = read_data()
    new_bus = request.get_json()
    
    if not new_bus or 'id' not in new_bus:
        return jsonify({"error": "Invalid bus data. 'id' is required."}), 400
        
    data['buses'].append(new_bus)
    write_data(data)
    return jsonify({"message": "Bus added successfully", "bus": new_bus}), 201

@app.route('/deleteBus/<bus_id>', methods=['DELETE']) # DELETE a bus
def delete_bus(bus_id):
    """Deletes a bus by its ID."""
    data = read_data()
    initial_length = len(data['buses'])
    
    # Filter out the bus with the matching ID
    data['buses'] = [b for b in data['buses'] if b['id'] != bus_id]
    
    if len(data['buses']) < initial_length:
        write_data(data)
        return jsonify({"message": f"Bus {bus_id} deleted successfully."}), 200
        
    return jsonify({"error": "Bus not found."}), 404

# --- Endpoints for Stops ---
@app.route('/getStops', methods=['GET']) # GET the list of stops
def get_stops():
    """Returns the list of stops."""
    data = read_data()
    return jsonify(data.get('stops', [])), 200

@app.route('/addStop', methods=['POST']) # ADD a new stop
def add_stop():
    """Adds a new stop to the configuration."""

    data = read_data()
    new_stop = request.get_json()
    
    if not new_stop or 'id' not in new_stop:
        return jsonify({"error": "Invalid stop data. 'id' is required."}), 400
        
    data['stops'].append(new_stop)

    write_data(data)
    return jsonify({"message": "Stop added successfully", "stop": new_stop}), 200


@app.route('/deleteStop', methods=['DELETE']) # DELETE a stop by ID
def delete_stop():
    """Deletes a stop by its ID sent in the JSON payload."""
   
    payload = request.get_json()
    
    
    stop_id = payload.get('stop_id') 
    
    if not stop_id:
        return jsonify({"error": "Nessun stop_id fornito"}), 400

    data = read_data()
    initial_length = len(data['stops'])
    
    
    data['stops'] = [s for s in data['stops'] if s['id'] != stop_id]
    
    if len(data['stops']) < initial_length:
        write_data(data)
        return jsonify({"message": f"Stop {stop_id} deleted successfully."}), 200
        
    return jsonify({"error": "Stop not found."}), 404


# --- Endpoints for City Params ---
@app.route('/updateCityParams', methods=['POST']) # MODIFY city parameters
def update_city_params():
    """Aggiorna i parametri della città."""
    data = read_data()
    new_params = request.get_json()
    
    # Update the values in the existing city_params
    data['city_params'] = new_params
    write_data(data)
    
    return jsonify({"message": "City params updated successfully", "city_params": new_params}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
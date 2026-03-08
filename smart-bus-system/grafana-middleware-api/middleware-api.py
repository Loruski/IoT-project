from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from flask import Flask, request, jsonify, Response
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "smart"
org = "univaq"
token = os.getenv("INFLUX_TOKEN")
url="http://20.0.0.40:8086"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

app = Flask(__name__)
CORS(app)
app.json.sort_keys = False


# Indirizzo base del config-api. 
# Usiamo l'IP statico definito nel docker-compose.yml sulla porta 5001.
CONFIG_API_URL = "http://20.0.0.12:5001" 

@app.route('/getBuses', methods=['GET'])
def get_buses():
    """Richiede la lista dei bus al config-api"""
    try:
        response = requests.get(f"{CONFIG_API_URL}/getBuses")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500

@app.route('/addBus', methods=['POST'])
def add_bus():
    """Inoltra la richiesta di aggiunta bus al config-api"""
    try:
        response = requests.post(f"{CONFIG_API_URL}/addBus", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500

@app.route('/deleteBus', methods=['DELETE'])
def delete_bus():
    """Inoltra la richiesta di eliminazione bus al config-api inviando il payload JSON."""
    try:
        # Passiamo il JSON ricevuto direttamente alla richiesta requests.delete
        response = requests.delete(f"{CONFIG_API_URL}/deleteBus", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500

# --- Endpoints for Stops ---
@app.route('/getStops', methods=['GET'])
def get_stops():
    """Richiede la lista degli stop al config-api"""
    try:
        stop_info = []
        response = requests.get(f"{CONFIG_API_URL}/getStops")
        for stop in response.json():
            stop_info.append(get_last_influx_stop_info(stop))
            
        json_string = json.dumps(stop_info)
        return Response(json_string, mimetype='application/json'), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500

@app.route('/addStop', methods=['POST'])
def add_stop():
    """Inoltra la richiesta di aggiunta stop al config-api"""
    try:
        response = requests.post(f"{CONFIG_API_URL}/addStop", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500

@app.route('/deleteStop', methods=['DELETE'])
def delete_stop():
    """Inoltra la richiesta di eliminazione stop al config-api inviando il payload JSON"""
    try:
        response = requests.delete(f"{CONFIG_API_URL}/deleteStop", json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Errore di comunicazione con config-api: {e}"}), 500
    
# --- Influx DB functions ---

def get_last_influx_stop_info(stop):
    """Recupera le ultime informazioni di un bus da InfluxDB con una singola query."""
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "busStop")
        |> filter(fn: (r) => r["bus_stop"] == "{stop['id']}")
        |> filter(fn: (r) => r["_field"] == "people" or r["_field"] == "rain" or r["_field"] == "temp")
        |> last()
        |> pivot(rowKey:["bus_stop"], columnKey: ["_field"], valueColumn: "_value")
    '''

    result = query_api.query(org=org, query=query)

    returnStop = {
        'id': str(stop['id']),
        'name': str(stop['name']),
        'people': None,
        'rain': None,
        'temp': None,
        'latitude': float(stop['lat']),
        'longitude': float(stop['lon'])
    }


    if result and len(result) > 0 and len(result[0].records) > 0:
        record = result[0].records[0]
        
        people_val = record.values.get("people")
        rain_val = record.values.get("rain")
        temp_val = record.values.get("temp")
        
        if people_val is not None:
            returnStop['people'] = int(people_val)
        if rain_val is not None:
            returnStop['rain'] = float(rain_val)
        if temp_val is not None:
            returnStop['temp'] = float(temp_val)

    return returnStop
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
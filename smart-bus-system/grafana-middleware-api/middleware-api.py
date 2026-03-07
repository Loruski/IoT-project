from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
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
        response = requests.get(f"{CONFIG_API_URL}/getStops")
        return jsonify(response.json()), response.status_code
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
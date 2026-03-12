# Project information

## Initial configuration

At first run a .env file is needed, and it's to be placed in the same folder where the yml docker compose file is present. This is in order to configure parameters such as admin username and password, network, without changing them in all docker containers.
The .env format is as follows:

```env
IOT_USERNAME = "admin"
IOT_PASSWORD = "admin123" # needs to be longer than 5 characters in order for influxdb to work correctly
INFLUX_TOKEN = "apjbchV0DxiMqyLFGxZPrNe1BtsRCKyfrAKGWjG5tngI0LwvCsKPMrL7UNZxLtliljCvHqJaueMMqULQ7yt1Zw==" #(for the database)
NETWORK = "21.0.0"#.0 (for the network in which the compose is declared)
MAIL_KEY="xxx.xxx.xxx.xxx" #(for the mailing service )
MAIL_LOGIN = "xxx@xxx.xxx.xxx"
```


### Config file
A config json file is specified and necessary in order for the sensor simulator to work and generate data to forward through the pipeline, the JSON format is as follows:

```json
{
  "city_params": {
    "rain_factor": 1.2, // likelihood of rain at stops, range from 0 to 10
    "global_temp": 22 // general baseline temperature of the cityscape in the simulation
  },
  "buses": [ // JSON-array of buses
    {
      "id": "B1", // UNIQUE identifier and name
      "route": [ // list of IDs of stops in order of travel (when arrived at last stop, it loops)
        "Stop4",
        "Stop2",
        "Stop3"
      ],
      "capacity": 50 // amount of people the bus can handle
    }, ...
    
  ],
  "stops": [ // JSON-array of stops
    {
      "id": "Stop1", // UNIQUE identifier
      "lat": 42.36778027625135, // latitude of the geographical position of the stop
      "lon": 13.352363241348343, // longitude of the geographical position of the stop
      "name": "Coppito" // name of the stop, no restrictions, it's used to identify the stop from the dashboards
    }, ...
  ]
}
```



## Data flow

```
Sensors --> MQTT --> Nodered --> InfluxDB
  /\                                ||
  ||                                || 
  \/                                \/                                 
Config API <-------------------> Middleware API <--> Grafana
```
 
### Config API
The api is created in python using Flask

- Expose the api to read and modify the JSON configuration
- Used by
    - Sensors simulator
    - Middleware API to add and delete buses and stops

### Sensors
- Simulate values for buses and stops
- Send values to an MQTT Broker with appropriate topics
- Bus sensors sends:
    - Bus status
    - Bus current stop
    - People inside the bus
- Stops sensors sends:
    - Rain 
    - Temperature
    - People waiting for the bus

```py
# Constants to easly format the topics adresses

# Topics
BUS = "bus"
STOP = "stop"

# Sensor types for stops
TEMP = "temp"
RAIN = "rain"
PEOPLE = "people" #People waiting for the bus

# Sensor types for buses
CURRENT_STOP = "current_stop"
CURRENT_CAPACITY = "current_capacity" #People inside the bus
STATUS = "status"
```

The topics have the following structure:
- `stop/{stop_id}/{sensor_type}/`
- `bus/{bus_id}/{sensor_type}/`

The `Bus Status` and the `People inside the bus` quantities are used to create alerts

### Mosquitto

The mosquitto server for hosting the MQTT broker is configured through the ``mosquitto.conf`` file in the directory `mosquitto/config` and authentication is enabled through the declaration of the line ```password_file /mosquitto/config/mosquitto.passwd```.
The `mosquitto.passwd` file is generated at build-time through the Dockerfile command:

```Dockerfile
RUN mosquitto_passwd -b -c /mosquitto/config/mosquitto.passwd $IOT_USERNAME $IOT_PASSWORD
```

Using the already specified username and password in the .env file.

### Middleware API

The middleware is an api with the purpose to connect grafana with the config, so the user can add and remove buses and stops. The middleware have also the role to join data from influx with static data from the json configuration


### Node red
in node red are defined 3 environment variables:
- MQTT_USERNAME
- MQTT_PASSWORD
- INFLUX_TOKEN

They're used in the nodes using the following format: ${ENVIRONMENT_VARIABLE}

They're used respectively for authentication towards the mqtt broker from which to get and process data, and for authentication towards InfluxDB, where the data is forwarded and stored.

NodeRed have the role of a data ingestor, joining all MQTT topics in two differents Json, one for buses and one for stops, and send this datas to influxDB

### InfluxDB

The data is stored in the bucket called `smart`, the correct way to visualize the structure of the data is as follows:
```
smart (bucket)
│
└───autobus
│   └───B1
│   │   │─── current_capacity
│   │   │─── current_stop
│   │   └─── status
│   └───B2
│   │   └─── ...
│   └─── ...
└───busStop
    └───Stop1
    │   │─── people
    │   │─── rain
    │   └─── temp
    └───Stop2
    │   └─── ...
    └─── ...
```

### Grafana

Grafana is used for hosting the dashboards for visualizing the data simulated and collected through the previous layers, 3 dashboards are created:

- **Buses Dashboard**: For visualize only the infos about buses, and also add and remove a bus
- **Data and general dashboard**: For visualizing an overview of both stops and buses, there's a map displaying their position, there also gaudges to display median values of all sensors, display the genereted alerts and also tables to display various info about buses and stops
- **Stops Dashboard**: For visualize only the infos about stops, and also add and remove a stops

**Used Plugins:**
- **yesoreyeram-infinity-datasource**: To create a REST API to middleware api
- **volkovlabs-form-panel**: To create forms to add and delete buses and stops

## Alerting System
The alerting system is implemented by grafana alert rules, the system send a telegram and email message to defined users, in particular:
- the alert system send a message if the quantity of people inside a bus is near the maximum capacity of a bus
- the alert system send a message if a bus have a failure
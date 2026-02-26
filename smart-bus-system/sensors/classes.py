class CityParams:
    def __init__(self, rain_factor ,global_temp):
        self.rain_factor = rain_factor
        self.global_temp = global_temp


class Bus:
    def __init__(self, id, route, capacity):
        self.id = id
        self.route:list[Stop] = route
        self.capacity:int = capacity
        self.currentStop:Stop | None = None


class Stop:
    def __init__(self, id, lat, lon, name):
        self.id = id
        self.lat:float = lat
        self.lon:float = lon
        self.name = name
        self.people:int = -1
        self.rain:float = -1
        self.temp:float = -254.0
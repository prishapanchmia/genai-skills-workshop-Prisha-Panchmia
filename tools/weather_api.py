import requests

CITY_COORDS = {
    "anchorage": (61.2181, -149.9003),
    "fairbanks": (64.8378, -147.7164),
    "juneau": (58.3019, -134.4197)
}

def get_weather(city: str) -> str:
    lat, lon = CITY_COORDS[city.lower()]
    url = f"https://api.weather.gov/points/{lat},{lon}"
    points = requests.get(url).json()
    forecast_url = points["properties"]["forecast"]
    forecast = requests.get(forecast_url).json()
    period = forecast["properties"]["periods"][0]
    return f"{period['name']}: {period['detailedForecast']}"
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_coords(city_name):
    """Converts a US City Name to Lat/Long using US Census Geocoder."""
    geo_url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={city_name}&benchmark=2020&format=json"
    try:
        res = requests.get(geo_url).json()
        address_matches = res['result']['addressMatches']
        if address_matches:
            coords = address_matches[0]['coordinates']
            return coords['y'], coords['x'] # latitude, longitude
    except:
        return None, None
    return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None

    if request.method == 'POST':
        city = request.form.get('city')
        lat, lon = get_coords(city)
        
        if lat and lon:
            # Step 1: Get the NWS grid points
            point_res = requests.get(f"https://api.weather.gov/points/{lat},{lon}").json()
            forecast_url = point_res['properties']['forecast']
            
            # Step 2: Get the actual forecast
            forecast_res = requests.get(forecast_url).json()
            current = forecast_res['properties']['periods'][0] # Latest period
            
            weather_data = {
                'temp': current['temperature'],
                'unit': current['temperatureUnit'],
                'desc': current['shortForecast'],
                'wind': f"{current['windSpeed']} {current['windDirection']}",
                'icon': current['icon'], # NWS provides a direct icon URL
                'detailed': current['detailedForecast']
            }

    return render_template('index.html', weather=weather_data, city=city)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

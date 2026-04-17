from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# IMPORTANT: Weather.gov requires a unique User-Agent string
HEADERS = {
    'User-Agent': '(my-weather-app, contact@example.com)'
}

def get_coords(city_name):
    """Uses OpenStreetMap Nominatim to find Lat/Long for a City Name."""
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None

    if request.method == 'POST':
        city = request.form.get('city')
        lat, lon = get_coords(city)
        
        if lat and lon:
            try:
                # Step 1: Get the NWS grid points
                point_url = f"https://api.weather.gov/points/{lat},{lon}"
                point_res = requests.get(point_url, headers=HEADERS).json()
                
                # Get the URL for the forecast
                forecast_url = point_res['properties']['forecast']
                
                # Step 2: Get the actual forecast data
                forecast_res = requests.get(forecast_url, headers=HEADERS).json()
                current = forecast_res['properties']['periods'][0]
                
                weather_data = {
                    'temp': current['temperature'],
                    'unit': current['temperatureUnit'],
                    'desc': current['shortForecast'],
                    'wind': f"{current['windSpeed']} {current['windDirection']}",
                    'icon': current['icon'],
                    'detailed': current['detailedForecast']
                }
            except Exception as e:
                print(f"Weather API error: {e}")
                city = f"Error: Could not fetch weather for {city}."

    return render_template('index.html', weather=weather_data, city=city)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
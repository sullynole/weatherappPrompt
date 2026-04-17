from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # ?format=j1 returns a rich JSON response
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                weather_data = {
                    'temp': current['temp_C'],
                    'desc': current['weatherDesc'][0]['value'],
                    'humidity': current['humidity'],
                    'wind': current['windspeedKmph'],
                    'feels_like': current['FeelsLikeC']
                }

    return render_template('index.html', weather=weather_data, city=city)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

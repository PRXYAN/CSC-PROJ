import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# --- IMPORTANT ---
API_KEY = '95a4f77bebe5409283860252250111' 
# ---------------

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None  

    if request.method == 'POST':
        city = request.form.get('city')
        
        url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            
            # --- THIS DICTIONARY IS NOW EXPANDED ---
            weather_data = {
                'location': data['location']['name'],
                'region': data['location']['region'],
                'country': data['location']['country'],
                'localtime': data['location']['localtime'],
                'temp': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon'],
                'feelslike': data['current']['feelslike_c'], # <-- New
                'humidity': data['current']['humidity'],   # <-- New
                'wind_kph': data['current']['wind_kph'],     # <-- New
                'wind_dir': data['current']['wind_dir']      # <-- New
            }
        else:
            weather_data = {'error': 'City not found. Please try again.'}

    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
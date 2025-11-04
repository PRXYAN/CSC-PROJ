import requests
from flask import Flask, render_template, request
from datetime import datetime 

app = Flask(__name__)

# --- IMPORTANT ---
API_KEY = '95a4f77bebe5409283860252250111' 
# ---------------

# --- (All helper functions like get_clothing_advice remain unchanged) ---
def get_clothing_advice(temp, feelslike, condition):
    condition = condition.lower()
    if 'rain' in condition or 'drizzle' in condition:
        return "🌧️ It's raining! Don't forget your umbrella and a waterproof jacket."
    if temp < 5 or feelslike < 0:
        return "🥶 Brr! It's very cold. Wear a heavy coat, scarf, and gloves."
    if temp < 12 or feelslike < 10:
        return "🧥 It's chilly. A warm jacket or sweater is a good idea."
    if temp > 28 and 'sunny' in condition:
        return "☀️ It's hot and sunny! Wear light clothes, a hat, and sunglasses."
    if temp > 22:
        return "👕 It's warm. A t-shirt and shorts/pants will be comfortable."
    return "👍 A light jacket or sweater should be perfect."

def get_aqi_advice(aqi_index):
    aqi_map = {
        1: ("Good", "Air quality is great! Perfect day to be outside."),
        2: ("Moderate", "Air quality is acceptable. Good for most, but sensitive groups should limit heavy outdoor exertion."),
        3: ("Unhealthy (Sensitive)", "Sensitive groups may experience health effects. Limit prolonged outdoor exertion."),
        4: ("Unhealthy", "Everyone may begin to experience health effects. Limit outdoor exertion."),
        5: ("Very Unhealthy", "Health alert: everyone may experience more serious health effects. Avoid outdoor exertion."),
        6: ("Hazardous", "Health warning of emergency conditions. The entire population is likely to be affected. Remain indoors.")
    }
    return aqi_map.get(aqi_index, ("Unknown", "AQI data not available."))

def get_activity_suggestion(temp, condition):
    condition = condition.lower()
    if 'rain' in condition or 'snow' in condition or 'storm' in condition:
        return "Indoor day! How about visiting a museum, baking, or working on your coding project? 😉"
    if 'sunny' in condition and temp > 18 and temp < 28:
        return "It's beautiful out! Great day for a picnic, a bike ride, or reading in the park."
    if 'windy' in condition and temp > 15:
        return "It's windy! Perfect weather to fly a kite."
    if temp < 5:
        return "It's very cold, but a brisk walk can be refreshing if you bundle up!"
    return "A pleasant day for a walk or running errands."
# --- End of helper functions ---


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None  

    if request.method == 'POST':
        city = request.form.get('city')
        url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3&aqi=yes'
        
        try:
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()
            
            current = data.get('current', {})
            location = data.get('location', {})
            forecast = data.get('forecast', {}).get('forecastday', [])
            today_astro = forecast[0].get('astro', {})
            
            # --- THIS IS WHERE WE GET AQI DATA ---
            aqi_data = current.get('air_quality', {})
            aqi_index = aqi_data.get('us-epa-index')
            # --------------------------------------

            temp_c = current.get('temp_c')
            feelslike_c = current.get('feelslike_c')
            condition_text = current.get('condition', {}).get('text', 'N/A')

            clothing_advice = get_clothing_advice(temp_c, feelslike_c, condition_text)
            aqi_meaning, aqi_advice = get_aqi_advice(aqi_index)
            activity_suggestion = get_activity_suggestion(temp_c, condition_text)
            
            forecast_list = []
            for day_data in forecast:
                day_name = datetime.fromtimestamp(day_data['date_epoch']).strftime('%A')
                day_info = {
                    'day_name': day_name,
                    'date': day_data.get('date'),
                    'maxtemp': day_data.get('day', {}).get('maxtemp_c'),
                    'mintemp': day_data.get('day', {}).get('mintemp_c'),
                    'condition': day_data.get('day', {}).get('condition', {}).get('text'),
                    'icon': day_data.get('day', {}).get('condition', {}).get('icon')
                }
                forecast_list.append(day_info)
            
            # --- UPDATED DICTIONARY ---
            weather_data = {
                # Current & Location
                'location': location.get('name'),
                'region': location.get('region'),
                'localtime': location.get('localtime'),
                'temp': temp_c,
                'condition': condition_text,
                'icon': current.get('condition', {}).get('icon'),
                'feelslike': feelslike_c,
                'humidity': current.get('humidity'),
                'wind_kph': current.get('wind_kph'),
                'wind_dir': current.get('wind_dir'),
                'pressure_mb': current.get('pressure_mb'),
                'uv': current.get('uv'),
                'vis_km': current.get('vis_km'),
                
                # Today's Astro Data
                'sunrise': today_astro.get('sunrise'),
                'sunset': today_astro.get('sunset'),
                
                # Unique Advice
                'aqi_index': aqi_index,
                'aqi_meaning': aqi_meaning,
                'aqi_advice': aqi_advice,
                'clothing_advice': clothing_advice,
                'activity_suggestion': activity_suggestion,
                
                # 3-Day Forecast List
                'forecast': forecast_list,
                
                # --- NEW RAW AQI DATA ---
                'aqi_co': aqi_data.get('co'),
                'aqi_no2': aqi_data.get('no2'),
                'aqi_o3': aqi_data.get('o3'),
                'aqi_so2': aqi_data.get('so2'),
                'aqi_pm2_5': aqi_data.get('pm2_5'),
                'aqi_pm10': aqi_data.get('pm10')
            }
        
        except requests.exceptions.HTTPError:
            weather_data = {'error': 'City not found or API error. Please try again.'}
        except Exception as e:
            weather_data = {'error': f'An unexpected error occurred: {e}'}

    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
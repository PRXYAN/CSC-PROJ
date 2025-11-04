import requests
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# --- IMPORTANT ---
# Replace this with your actual API key from WeatherAPI.com
API_KEY = 'YOUR_API_KEY_GOES_HERE' 
# ---------------

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None  # Initialize weather_data to None

    # This block runs when the user submits the form
    if request.method == 'POST':
        city = request.form.get('city')
        
        # Make the API call
        url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}'
        response = requests.get(url)

        # If the API call was successful
        if response.status_code == 200:
            data = response.json()
            # Organize the data we need into a dictionary
            weather_data = {
                'location': data['location']['name'],
                'temp': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon']
            }
        else:
            # Handle cases where the city is not found or API fails
            weather_data = {'error': 'City not found. Please try again.'}

    # This line runs on both GET (page load) and POST (form submit)
    # It passes the 'weather_data' to the HTML
    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
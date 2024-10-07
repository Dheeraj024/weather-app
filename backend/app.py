from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg2

app = Flask(__name__)
CORS(app)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="weatherapp_db",
    user="weatherapp_user",
    password="your_password"
)
cursor = conn.cursor()

# Create table for storing search history
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_searches (
    id SERIAL PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    weather_data JSONB,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()



@app.route('/api/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    # Fetch weather data from OpenWeatherMap API
    api_key = 'cf2b289f9f9aa4a891669bfa17ef28c8'
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch weather data'}), 500

    weather_data = response.json()

    # Insert search data into PostgreSQL
    cursor.execute(
        "INSERT INTO weather_searches (latitude, longitude, weather_data) VALUES (%s, %s, %s)",
        (lat, lon, weather_data)
    )
    conn.commit()

    return jsonify(weather_data), 200


@app.route('/api/history', methods=['GET'])
def get_history():
    cursor.execute("SELECT latitude, longitude, weather_data, search_time FROM weather_searches ORDER BY search_time DESC")
    rows = cursor.fetchall()

    history = []
    for row in rows:
        history.append({
            'latitude': row[0],
            'longitude': row[1],
            'weather_data': row[2],
            'search_time': row[3]
        })

    return jsonify(history), 200




if __name__ == '__main__':
    app.run(debug=True)

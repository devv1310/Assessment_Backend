from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

# Database setup
DB_PATH = 'database/chatbot.db'

def init_db():
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# API Configuration
OPENWEATHER_API_KEY = "your_openweathermap_api_key"  # Replace with your OpenWeatherMap API Key
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/message', methods=['POST'])
def get_response():
    user_message = request.json.get('message', '').lower()

    # Default response
    bot_response = "Sorry, I didn't understand that."

    # Response logic with live API integration
    if "hello" in user_message:
        bot_response = "Hello! How can I assist you?"
    elif "bye" in user_message:
        bot_response = "Goodbye! Have a wonderful day!"
    elif "how are you" in user_message:
        bot_response = "I'm just a bot, but I'm here to help you!"
    elif "your name" in user_message:
        bot_response = "I'm ChatBot, your virtual assistant."
    elif "help" in user_message:
        bot_response = "Sure, let me know what you need help with."
    elif "time" in user_message:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        bot_response = f"The current time is {current_time}."
    elif "date" in user_message:
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        bot_response = f"Today's date is {current_date}."
    elif "joke" in user_message:
        bot_response = "Why don't skeletons fight each other? They don't have the guts!"
    elif "weather" in user_message:
        # Extract city from user message
        city = user_message.replace("weather", "").strip()
        if not city:
            bot_response = "Please specify a city to get the weather information."
        else:
            # Fetch live weather data
            try:
                response = requests.get(WEATHER_API_URL, params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                })
                if response.status_code == 200:
                    data = response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    bot_response = f"The current temperature in {city.title()} is {temp}°C with {description}."
                else:
                    bot_response = f"Could not retrieve weather for {city.title()}. Please check the city name."
            except Exception as e:
                bot_response = "I'm having trouble fetching the weather right now. Please try again later."

    # Save the messages to the database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO messages (user_message, bot_response) VALUES (?, ?)', 
              (user_message, bot_response))
    conn.commit()
    conn.close()

    return jsonify({'bot_response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)


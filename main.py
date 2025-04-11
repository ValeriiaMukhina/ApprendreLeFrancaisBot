import os
import asyncio
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder

# Import your bot logic from bot.py (ensure that bot.py does not call run_polling() directly)
from bot import run_bot  # Suppose you refactor your bot start logic to a run_bot() function

# Create a Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    # Run the Flask server in a separate thread
    Thread(target=run).start()
    # Run your Telegram bot (this might be an asyncio run call)
    asyncio.run(run_bot())

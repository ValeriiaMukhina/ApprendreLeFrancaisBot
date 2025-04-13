import os
import asyncio
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder

from bot import run_bot 

# Define a simple Flask application
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Define the run_web function to start the Flask server
def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run_web).start()
    # Run the bot synchronously.
    run_bot()

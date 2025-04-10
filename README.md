# Language Learning Telegram Bot

A Telegram-based chatbot designed to help users practice French translation by converting dynamically generated Ukrainian sentences. This interactive bot leverages OpenAI’s language models to generate translation exercises and evaluate user translations—providing corrected translations along with detailed explanations and comments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

This project is an interactive language-learning tool that allows users to improve their French translation skills. The bot:
- Generates a Ukrainian sentence based on topics (vocabulary and grammar) derived from the EditoB1 textbook.
- Prompts users to translate the sentence into French.
- Evaluates the translation using an OpenAI language model, returning corrections and detailed explanations of any errors.
- Automatically generates a new sentence for continuous practice within the same unit.

The exercises are dynamically tailored using a JSON file (`EditoB1.json`) that holds information for each unit (e.g., unit number, title, vocabulary, grammar topics).

## Features

- **Dynamic Sentence Generation:**  
  Generates targeted Ukrainian sentences for translation practice based on unit-specific vocabulary and grammar topics.
  
- **Translation Evaluation & Feedback:**  
  Accepts user translations and leverages OpenAI’s models (GPT‑3.5 Turbo or GPT‑4) to verify correctness, correct errors, and provide detailed commentary.
  
- **Continuous Practice:**  
  After evaluating a translation, the bot automatically sends a new sentence from the same unit for further practice.
  
- **Telegram Integration:**  
  Fully integrated with Telegram using the `python-telegram-bot` library, allowing for a seamless conversational user interface.

## Prerequisites

Before running the project, ensure you have:

- **Python 3.7+**
- A **Telegram Bot token** from [BotFather](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
- An **OpenAI API key** (trial or paid) from the [OpenAI platform](https://platform.openai.com)
- Git installed for version control

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/language-bot-project.git
   cd language-bot-project
2. **Set Up a Virtual Environment:**

   ```bash
   python3 -m venv env
3. **Activate the Virtual Environment:**

   ```bash
   On Windows: env\Scripts\activate
   On macOS/Linux: source env/bin/activate

4. **Install Dependencies:**
 
   ```bash
   pip install -r requirements.txt 


5. **Configure Environment Variables:**

    Create a .env file in the project root with the following content:

   ```bash
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here

    ```
    
## Usage
Run the Bot:

With your virtual environment activated, run:

   ```bash
   python bot.py
   ```

Interact via Telegram:

Start the Bot: Type /start to begin.

Begin an Exercise: Type /exercise <unit_number> (e.g., /exercise 1) to receive a Ukrainian sentence.

Submit Your Translation: Reply with your French translation. The bot will evaluate your input and send back corrections and explanations, then prompt you with a new sentence from the same unit.
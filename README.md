# Language Learning Telegram Bot

Imagine a dynamic language-learning experience that transforms everyday YouTube videos into a personalized French translation exercise! Our Telegram-based chatbot empowers you to master French by leveraging real-world video content. Here’s what makes it truly unique:

- Seamless YouTube Integration:
Simply share a YouTube video link, and the bot automatically extracts the transcript using cutting-edge technology. No more manual copying—just fast, accurate transcript extraction at your fingertips.

- Tailored Language Learning:
The bot uses OpenAI’s language models to pinpoint and extract the most useful French phrases from the video transcript, complete with Ukrainian translations. These phrases are customized to your specific proficiency level, ranging from A1 to C2, ensuring that the learning content is perfectly suited to your needs.

- Interactive Translation Practice:
Once the useful phrases are presented, the chatbot challenges you with real translation exercises. It generates concise Ukrainian sentences that incorporate key vocabulary and grammar from the video content. Your task is to translate these sentences into French.

- Instant, Intelligent Feedback:
After you submit your translation, the bot doesn’t just check your work—it provides detailed corrections and explanations. Discover exactly where you went astray and how to improve, all in real time.

- Continuous, Adaptive Exercises:
Learning never stops! As soon as your translation is evaluated, the bot automatically generates a new exercise, keeping you immersed in a productive learning cycle. And if you ever want to change the content, simply enter a new YouTube link or cancel the current session with a command.

- User-Friendly and Engaging:
Built on Telegram, the chatbot provides a smooth, conversational interface that makes language learning both fun and interactive. Whether you’re a beginner or an advanced learner, the experience adapts to your pace and style of learning.

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

This project is an advanced language-learning tool designed for French learners. Instead of relying on preloaded content, the bot uses a YouTube video link provided by the user to:
- Extract a transcript from the video.
- Identify and extract useful French phrases (with Ukrainian translations) that are appropriate for a specific language level (A1, A2, B1, B2, C1, C2).
- Offer a series of translation exercises where the user translates Ukrainian sentences into French.
- Provide immediate feedback by verifying the translation, correcting mistakes, and explaining errors.
- Allow users to reset the session and submit a new video link at any time.


## Features

- **Dynamic Content Extraction:**  
  Automatically extracts the transcript from any provided YouTube video using the `youtube_transcript_api`.

- **Adaptive Language Support:**  
  Tailors the extracted useful phrases according to the student’s level (A1 through C2) using OpenAI’s language models.

- **Interactive Translation Exercises:**  
  Generates Ukrainian sentences based on the extracted vocabulary for the student to translate into French.

- **Automated Feedback:**  
  Verifies the user's translation, returning the correct translation along with explanations of any errors.

- **Session Management:**  
  Users can start a new session with a new YouTube link at any time by using commands such as `/cancel` or `/newlink`.


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

- Start the Conversation:
Send the /start command. The bot will ask for a YouTube video link.

- Submit a Video Link:
Provide the YouTube URL. The bot will fetch the transcript automatically.

- Select Your Level:
Next, you’ll be prompted to enter your level (A1, A2, B1, B2, C1, or C2).

- Receive Useful Phrases:
The bot will extract and display a list of useful French phrases (with Ukrainian translations) from the video transcript.

- Choose to Practice:
When prompted, type Yes to begin translation exercises based on the extracted phrases.

- Translation Exercise:
The bot will generate a Ukrainian sentence for you to translate into French. After you send your translation, the bot will verify it, provide corrections and explanations, and then automatically generate another sentence for you to translate.

- Reset or Enter New Video:
At any time, use the /cancel or /newlink command to end the current session and start over with a new YouTube link.
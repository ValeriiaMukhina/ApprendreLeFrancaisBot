import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import json
import openai
import asyncio
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Enable logging to help with debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Your bot token from BotFather should be stored in a .env file as TELEGRAM_BOT_TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load the JSON file that contains your EditoB1 data
try:
    with open("EditoB1.json", "r", encoding="utf-8") as f:
        edito_data = json.load(f)
except Exception as e:
    print("Error loading JSON file:", e)
    edito_data = None


# Dictionary to store current exercise per chat (keyed by chat_id)
current_exercises = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your language learning bot. How can I help you today?")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function echoes the user message (for testing purposes)
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

async def list_units(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the JSON data loaded successfully
    if not edito_data or "units" not in edito_data:
        await update.message.reply_text("Sorry, the unit data is not available at the moment.")
        return

    # Build a message that lists the units with their titles
    units = edito_data["units"]
    message_text = "Available Units:\n"
    for unit in units:
        # Example: "Unité 1: Introductions & Daily Life"
        message_text += f"{unit['unit']}: {unit['title']}\n"

    await update.message.reply_text(message_text)

async def generate_exercise_sentence(unit_info):
    """
    Generate a Ukrainian sentence for a translation exercise based on the provided unit topics.
    """
    # Prepare the prompt using vocabulary and grammar topics from the unit
    vocabulary = ", ".join(unit_info.get("vocabulary", []))
    grammar = ", ".join(unit_info.get("grammar_topics", []))
    prompt = (
        f"Generate a concise Ukrainian sentence for a French translation exercise. "
        f"The sentence should incorporate the following vocabulary: {vocabulary} and "
        f"test these grammar topics: {grammar}. "
        "Return ONLY the Ukrainian sentence without any French translation or additional commentary."
    )

    try:
        # Use the asynchronous method via the client
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a creative language exercise generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        generated_sentence = response.choices[0].message.content.strip()
    except Exception as e:
        generated_sentence = f"Error generating sentence: {e}"
    return generated_sentence


async def send_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the user provided a unit number (e.g., /exercise 1)
    if not context.args:
        await update.message.reply_text("Please provide the unit number. E.g., /exercise 1")
        return

    unit_number = context.args[0]
    # Find the unit in edito_data that matches (assuming unit field contains the number)
    selected_unit = None
    for unit in edito_data["units"]:
        # We'll assume unit["unit"] contains e.g., "Unité 1"
        if unit_number in unit["unit"]:
            selected_unit = unit
            break

    if not selected_unit:
        await update.message.reply_text("Unit not found. Please check the unit number.")
        return

    # Generate a Ukrainian sentence dynamically using the LLM based on the unit's topics
    sentence = await generate_exercise_sentence(selected_unit)

    # Store the current exercise (using chat id as key) so we can verify later
    chat_id = update.message.chat_id
    current_exercises[chat_id] = {
        "unit": selected_unit,
        "ukrainian_sentence": sentence
    }

    await update.message.reply_text(
        f"Translate the following sentence into French:\n\n{sentence}\n\nPlease reply with your translation."
    )

async def verify_translation(ukrainian_sentence, user_translation, unit_info):
    """
    Verify the user's French translation of a Ukrainian sentence.
    Provides the corrected translation and detailed explanations of errors.
    """
    # Prepare vocabulary and grammar details for the prompt
    vocabulary = ", ".join(unit_info.get("vocabulary", []))
    grammar = ", ".join(unit_info.get("grammar_topics", []))
    
    # Build the prompt for the LLM
    prompt = (
        f"You are a helpful French language tutor specializing in translation. "
        f"A student was given the following Ukrainian sentence to translate into French:\n"
        f"Ukrainian: \"{ukrainian_sentence}\"\n"
        f"The student's French translation is: \"{user_translation}\"\n\n"
        f"This unit covers vocabulary such as: {vocabulary} and grammar topics including: {grammar}.\n\n"
        "Please do the following:\n"
        "1. Provide the correct translation.\n"
        "2. Explain in detail any errors made by the student and why the correction is needed.\n"
        "Your explanation should refer to the vocabulary and grammar topics when relevant."
    )
    
    try:
        # Use our asynchronous client to call the ChatCompletion endpoint
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are a helpful French language tutor and translation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        feedback = response.choices[0].message.content.strip()
    except Exception as e:
        feedback = f"Error verifying translation: {e}"
    return feedback

async def handle_translation_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler that processes the user's translation, verifies it, sends feedback,
    and then generates a new exercise sentence for the same unit.
    """
    chat_id = update.message.chat_id

    # Check if an exercise session is active for this chat
    if chat_id not in current_exercises:
        await update.message.reply_text("Please start an exercise first using /exercise <unit_number>.")
        return

    # Retrieve the current exercise details and remove the old session
    exercise_data = current_exercises.pop(chat_id)
    ukrainian_sentence = exercise_data["ukrainian_sentence"]
    unit_info = exercise_data["unit"]

    # Get the user's translation
    user_translation = update.message.text

    # Inform the user we're processing the translation
    await update.message.reply_text("Processing your translation, please wait...")

    # Verify the translation and get the feedback from the LLM
    feedback = await verify_translation(ukrainian_sentence, user_translation, unit_info)
    await update.message.reply_text(feedback)

    # Generate a new exercise sentence for the same unit
    new_sentence = await generate_exercise_sentence(unit_info)
    
    # Save the new session for the chat using the same unit
    current_exercises[chat_id] = {
        "unit": unit_info,
        "ukrainian_sentence": new_sentence
    }
    
    # Send the new exercise sentence to the user
    await update.message.reply_text(
        f"Next sentence for translation:\n\n{new_sentence}\n\nPlease provide your translation."
    )



if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers for different commands and messages
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(start_handler)
    application.add_handler(CommandHandler("units", list_units))
    application.add_handler(CommandHandler("exercise", send_exercise))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translation_response))


    # Start the bot
    print("Bot is running...")
    application.run_polling()

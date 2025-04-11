import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI
import youtube_utils 

# Load environment variables from .env file
load_dotenv()

# Enable logging to help with debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

VIDEO, LEVEL, ASK_EXERCISE, TRANSLATION = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your language learning bot. How can I help you today?")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function echoes the user message (for testing purposes)
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")


async def extract_useful_phrases(transcript, level):
    prompt = (
        f"Extract a list of useful French phrases for a level {level} learner "
        f"from the following video transcript. For each phrase, provide its translation into Ukrainian.\n\nTranscript:\n{transcript}\n\n"
        "Return the result in a bullet list format."
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert French language teacher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error extracting useful phrases: {e}"

async def generate_exercise_sentence_from_phrases(phrases, level):
    prompt = (
        f"Based on the following useful French phrases for a level {level} learner:\n\n{phrases}\n\n"
        "Generate a concise Ukrainian sentence that a French learner should translate into French. "
        "The sentence should include at least one of the phrases and be appropriate for the student's level."
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative language exercise generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating exercise sentence: {e}"

async def verify_translation(original_sentence, user_translation, phrases, level):
    prompt = (
        f"You are a French language tutor. A student was given the following exercise:\n\n"
        f"Original Ukrainian sentence: \"{original_sentence}\"\n"
        f"Student's French translation: \"{user_translation}\"\n\n"
        f"Useful phrases (with Ukrainian translations) for level {level}: {phrases}\n\n"
        "Provide the correct translation, point out any errors in the student's translation, "
        "and explain the corrections."
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful French language tutor and translation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error verifying translation: {e}"


# Start command handler: ask for YouTube link
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! Please send me a YouTube video link.")
    return VIDEO

# Handle video link input
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_url = update.message.text
    try:
        # Fetch the transcript (try French, fallback to English if needed)
        transcript = youtube_utils.get_youtube_transcript(video_url, languages=['fr', 'en'])
        context.user_data['transcript'] = transcript
        context.user_data['video_url'] = video_url
        await update.message.reply_text("Transcript loaded! Now, please specify your level (A1, A2, B1, B2, C1, or C2).")
        return LEVEL
    except Exception as e:
        await update.message.reply_text(f"Error obtaining transcript: {e}\nPlease send a valid YouTube link.")
        return VIDEO

# Handle level input
async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    level = update.message.text.upper().strip()
    if level not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        await update.message.reply_text("Invalid level. Please enter one of: A1, A2, B1, B2, C1, C2.")
        return LEVEL

    context.user_data['level'] = level

    # Extract useful phrases using the transcript and level
    transcript = context.user_data['transcript']
    phrases = await extract_useful_phrases(transcript, level)
    context.user_data['useful_phrases'] = phrases
    await update.message.reply_text(f"Here are some useful phrases for level {level}:\n\n{phrases}")

    # Ask if the user wants to practice exercises based on these phrases.
    reply_keyboard = [['Yes', 'No']]
    await update.message.reply_text("Would you like to practice exercises based on these phrases?",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ASK_EXERCISE

# Handle user's choice for exercise practice
async def exercise_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.lower()
    if choice == 'yes':
        level = context.user_data['level']
        phrases = context.user_data['useful_phrases']
        # Generate an exercise sentence using the extracted phrases.
        exercise_sentence = await generate_exercise_sentence_from_phrases(phrases, level)
        context.user_data['current_exercise'] = exercise_sentence
        await update.message.reply_text(
            f"Translate the following sentence into French:\n\n{exercise_sentence}")
        return TRANSLATION
    else:
        await update.message.reply_text("Alright, feel free to send a new video link whenever you're ready.")
        return ConversationHandler.END

# Handle user's translation responses
async def translation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_translation = update.message.text
    current_sentence = context.user_data.get('current_exercise')
    phrases = context.user_data.get('useful_phrases')
    level = context.user_data.get('level')
    if not current_sentence:
        await update.message.reply_text("There's no active exercise. Please start a new one with /start.")
        return ConversationHandler.END

    await update.message.reply_text("Processing your translation, please wait...")
    feedback = await verify_translation(current_sentence, user_translation, phrases, level)
    await update.message.reply_text(feedback)

    # Automatically generate a new exercise sentence from the same phrases.
    new_sentence = await generate_exercise_sentence_from_phrases(phrases, level)
    context.user_data['current_exercise'] = new_sentence
    await update.message.reply_text(
        f"Next sentence for translation:\n\n{new_sentence}")
    return TRANSLATION

# Cancel handler in case the user wants to abort the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    return ConversationHandler.END

async def new_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()  # Clear any previous session data
    await update.message.reply_text("You've chosen to enter a new video. Please send me your new YouTube link.")
    return VIDEO  # Reset the conversation state to expect a new video link.

# Create and add the conversation handler to your application
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, video_handler)],
        LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_handler)],
        ASK_EXERCISE: [MessageHandler(filters.Regex('^(Yes|No)$'), exercise_choice_handler)],
        TRANSLATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, translation_handler)]
    },
    fallbacks=[
        CommandHandler('cancel', cancel),
        CommandHandler('newlink', new_link)
    ]
)




if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('newlink', new_link))
    application.add_handler(CommandHandler('cancel', cancel))

    print("Bot is running...")
    application.run_polling()

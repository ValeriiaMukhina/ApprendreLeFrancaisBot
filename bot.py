import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI
import youtube_utils
from localization import MESSAGES
import asyncio

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

LANG, VIDEO, LEVEL, ASK_EXERCISE, TRANSLATION = range(5)




async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip().lower()
    if choice == 'english':
        context.user_data['lang'] = 'en'
    elif choice in ['українська', 'ukrainian']:
        context.user_data['lang'] = 'ua'
    else:
        context.user_data['lang'] = 'en'
    lang = context.user_data['lang']
    welcome_message = MESSAGES[lang]['welcome']
    # Open the local image file in binary mode
    with open("welcome_image.png", "rb") as photo_file:
        await update.message.reply_photo(photo=photo_file, caption=welcome_message)

    ask_youtube = MESSAGES[lang]['ask_youtube']
    await update.message.reply_text(ask_youtube)
    return VIDEO

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function echoes the user message (for testing purposes)
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")


async def extract_useful_phrases(transcript, level):
    prompt = (
        f"You are a qualified French teacher and native speaker.\n"
        f"Your task is to help a French learner at level {level} enrich their vocabulary and learn useful expressions from the video transcript below.\n"
        f"Please extract up to 15 useful words or short phrases that are appropriate for a learner at this level. These should be expressions that are common in daily life and helpful for everyday conversations.\n"

        f"For each one:\n"
        f"Provide the phrase in French\n"
        f"Give a natural, spoken-style Ukrainian translation that is both accurate and easy to understand\n"
        f"Transcript:\n"
        f"{transcript}\n"
        f"Output format:\n"
        f"French phrase — Ukrainian translation"
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
        f"You are a qualified French teacher preparing a translation exercise for a student at level {level}.\n\n"
        f"Based on the following list of useful French phrases:\n\n{phrases}\n\n"
        "Create one concise sentence in Ukrainian that the student should translate into French.\n"
        "- The sentence must include at least one phrase from the list.\n"
        "- It should be natural, relevant to everyday life, and appropriate for the student’s language level.\n"
        "- The goal is to help the learner practice using the phrase in context."
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

async def verify_translation(original_sentence, user_translation, phrases, level, lang):
    if lang == 'ua':
        prompt = (
            f"Ви — кваліфікований викладач французької мови.\n\n"
            f"Учневі було дано таке завдання:\n"
            f"- Оригінальне речення українською: \"{original_sentence}\"\n"
            f"- Переклад учня французькою: \"{user_translation}\"\n\n"
            f"Рівень учня: {level}. Ось корисні фрази, які він/вона вивчає: {phrases}\n\n"
            "Ваше завдання:\n"
            "1. Наведіть правильний переклад українського речення французькою мовою.\n"
            "2. Вкажіть помилки в перекладі учня.\n"
            "3. Поясніть кожну помилку зрозумілою українською мовою, простими словами, які підходять для учня."
        )
    else:
        prompt = (
            f"You are a qualified French language tutor.\n\n"
            f"A student was given the following exercise:\n"
            f"- Original Ukrainian sentence: \"{original_sentence}\"\n"
            f"- Student's French translation: \"{user_translation}\"\n\n"
            f"The student is at level {level}. The following are useful phrases they are learning: {phrases}\n\n"
            "Your task:\n"
            "1. Provide the correct French translation of the Ukrainian sentence.\n"
            "2. Point out any errors in the student's translation.\n"
            "3. Explain each correction clearly in English, using simple terms suitable for a learner."
        )
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful French language tutor and translation expert. "
                        "Respond in Ukrainian." if lang == 'ua' else "Respond in English."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error verifying translation: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Offer a keyboard for language selection
    reply_keyboard = [['English', 'Українська']]
    await update.message.reply_text(
        "Please choose your preferred language / Будь ласка, оберіть бажану мову:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return LANG

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video_url = update.message.text
    lang = context.user_data.get('lang', 'en')  # Get the selected language, default to English
    try:
        # Run the synchronous transcript function in a separate thread.
        transcript = await asyncio.to_thread(
            youtube_utils.get_youtube_transcript, video_url, ['fr', 'en']
        )
        context.user_data['transcript'] = transcript
        context.user_data['video_url'] = video_url
        # Retrieve the localized level prompt from the MESSAGES dictionary
        ask_level = MESSAGES[lang]['ask_level']
        await update.message.reply_text(ask_level)
        return LEVEL
    except Exception as e:
        await update.message.reply_text(f"Error obtaining transcript: {e}\n" + MESSAGES[lang]['ask_youtube'])
        return VIDEO

# Handle level input
async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    level = update.message.text.upper().strip()

    if level not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        await update.message.reply_text("Invalid level. Please enter one of: A1, A2, B1, B2, C1, C2.")
        return LEVEL

    context.user_data['level'] = level
    transcript = context.user_data['transcript']
    # Call your helper function to extract useful phrases
    phrases = await extract_useful_phrases(transcript, level)
    context.user_data['useful_phrases'] = phrases
    lang = context.user_data.get('lang', 'en')
    header = MESSAGES[lang]['useful_phrases_header'].format(level=level)
    await update.message.reply_text(f"{header}\n\n{phrases}")

    ask_exercise = MESSAGES[lang]['ask_exercise']
    reply_keyboard = [['Yes', 'No']] if lang == 'en' else [['Так', 'Ні']]
    await update.message.reply_text(
        ask_exercise,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_EXERCISE

# Handle user's choice for exercise practice
async def exercise_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.lower()
    lang = context.user_data.get('lang', 'en')
    if choice in ['yes', 'так']:
        level = context.user_data['level']
        phrases = context.user_data['useful_phrases']
        # Generate an exercise sentence using the extracted phrases.
        exercise_sentence = await generate_exercise_sentence_from_phrases(phrases, level)
        context.user_data['current_exercise'] = exercise_sentence
        lang = context.user_data.get('lang', 'en')
        translate_prompt = MESSAGES[lang]['translate_prompt']
        await update.message.reply_text(
            f"{translate_prompt}\n\n{exercise_sentence}"
        )
        return TRANSLATION
    else:
        await update.message.reply_text(MESSAGES[lang]['session_cancelled'])
        return ConversationHandler.END

# Handle user's translation responses
async def translation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_translation = update.message.text
    current_sentence = context.user_data.get('current_exercise')
    phrases = context.user_data.get('useful_phrases')
    level = context.user_data.get('level')
    lang = context.user_data.get('lang', 'en')
    
    if not current_sentence:
        await update.message.reply_text("There's no active exercise. Please start a new one with /start.")
        return ConversationHandler.END

    processing_msg = MESSAGES[lang]['processing']
    await update.message.reply_text(processing_msg)
    lang = context.user_data.get('lang', 'en')
    feedback = await verify_translation(current_sentence, user_translation, phrases, level, lang)
    await update.message.reply_text(feedback)

    # Automatically generate a new exercise sentence for continued practice.
    new_sentence = await generate_exercise_sentence_from_phrases(phrases, level)
    context.user_data['current_exercise'] = new_sentence
    new_sentence_msg = MESSAGES[lang]['new_sentence']
    await update.message.reply_text(f"{new_sentence_msg}\n\n{new_sentence}")
    return TRANSLATION

# Cancel handler in case the user wants to abort the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(MESSAGES[lang]['session_cancelled'])
    return ConversationHandler.END

async def new_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get('lang', 'en')  # Save the current language selection
    context.user_data.clear()                   # Clear all session data
    context.user_data['lang'] = lang            # Restore the language setting
    await update.message.reply_text(MESSAGES[lang]['new_link'])
    return VIDEO

# Create and add the conversation handler to your application
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        LANG: [MessageHandler(filters.Regex("^(English|Українська)$"), language_handler)],
        VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, video_handler)],
        LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_handler)],
        ASK_EXERCISE: [MessageHandler(filters.Regex("^(Yes|No|Так|Ні)$"), exercise_choice_handler)],
        TRANSLATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, translation_handler)]
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler('newlink', new_link)]
)

def run_bot():
    application = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('newlink', new_link))
    application.add_handler(CommandHandler('cancel', cancel))
    application.run_polling()


# Optional: if you want to run your bot directly from bot.py, you can add:
if __name__ == '__main__':
    run_bot()

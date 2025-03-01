import logging
import os
from pathlib import Path
from services.transcribe import transcribe_audio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler
from dotenv import load_dotenv
from io import BytesIO
import requests
from services.letter_action_identifier import extract_content, identify_letter_action, respond_to_query
from telegram.constants import ParseMode
from services.transcribe import transcribe_audio

load_dotenv()
# Constants for the conversation states
ALLERGENS = 0

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GENERATE_URL = os.getenv('GENERATE_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_sessions = {}
letter_contents = {}


welcome_message = """
I'm here to read your letter. Upload a photo of your letter and I will tell you what to do with it in Chinese.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_sessions[user_id] = []
    letter_contents[user_id] = []

    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_chat.id] = []
    letter_contents[update.effective_chat.id] = []

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Restarting a new chat session!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Goodbye!")


# async def save_allergens(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_chat.id
#     allergens_text = update.message.text
#     allergen_list = [item.strip() for item in allergens_text.split(',')]
    
#     user_allergens[user_id] = allergen_list
    
#     await context.bot.send_message(
#         chat_id=user_id,
#         text=f"Your allergens have been saved: {', '.join(allergen_list)}\nYou can update them anytime with /allergens."
#     )
#     return ConversationHandler.END

# async def talk_to_llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_chat.id
#     history = user_sessions[user_id]
#     user_msg = update.message.text
    
#     # Check if user has registered allergens
#     if user_id in user_allergens:
#         # Include the allergens in the system message or processing
#         allergens = user_allergens[user_id]
#         # Here you would integrate allergen info with your LLM request
#         # system_msg = get_reply_from_chatbot(user_msg, history, allergens)
#         system_msg = update.message.text
#     else:
#         system_msg = "Please set your allergens first using the /allergens command."
    
#     user_sessions[user_id] = history + [(user_msg, system_msg)]
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=system_msg)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    application = ApplicationBuilder().read_timeout(30).write_timeout(30).token(TELEGRAM_TOKEN).build()
    
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        # Get the photo with the highest resolution
        photo_file = await update.message.photo[-1].get_file()
        print(photo_file)
        photo_file_bytes = BytesIO(await photo_file.download_as_bytearray())

        
        # Acknowledge receipt of photo
        await context.bot.send_message(
            chat_id=user_id, 
            text="I received your photo. Let me see what actions you need to take."
        )
        

        letter_text = extract_content(photo_file_bytes, Path(photo_file.file_path).name)
        letter_contents[user_id] = letter_text

        letter_action_summary = identify_letter_action(letter_text)

        # For now, just send a placeholder response
        await context.bot.send_message(
            chat_id=user_id,
            text=letter_action_summary
        )

    
    # For voice message handling
    async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        history = user_sessions[user_id]

        if user_id not in letter_contents:
            await context.bot.send_message(
                chat_id=user_id, 
                text="Upload a photo of your letter first."
            )
            return


        letter_content = letter_contents[user_id]

        # Get the voice file
        voice_file = await update.message.voice.get_file()
        voice_file_bytes = BytesIO(await voice_file.download_as_bytearray())
        
        # Acknowledge receipt of voice message
        await context.bot.send_message(
            chat_id=user_id, 
            text="I received your voice message. Processing it now..."
        )
        
        try:
            transcription_response = transcribe_audio(voice_file_bytes, f"voice_{voice_file.file_unique_id}.ogg")
            transcription_response_text = transcription_response.text

            history.append({"role": "user", "content": transcription_response_text})

            query_answer = respond_to_query(letter_text=letter_content, chat_history=history)

            history.append({"role": "assistant", "content": query_answer})

            user_sessions[user_id] = history


            await context.bot.send_message(
                chat_id=user_id,
                text=query_answer,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logging.error(f"Error processing voice message: {str(e)}")
            await context.bot.send_message(
                chat_id=user_id,
                text="Sorry, I encountered an error processing your voice message."
            )
    
    # Add the photo handler to the application

    start_handler = CommandHandler('start', start)
    clear_handler = CommandHandler('clear', clear)
    stop_handler = CommandHandler('stop', stop)
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    voice_handler = MessageHandler(filters.VOICE, handle_voice)

    application.add_handler(start_handler)
    application.add_handler(clear_handler)
    application.add_handler(stop_handler)
    application.add_handler(voice_handler)
    application.add_handler(photo_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()
import logging
import os
from pathlib import Path
from services.transcribe import transcribe_audio
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler
from dotenv import load_dotenv
from io import BytesIO
from services.letter_action_identifier import extract_content, identify_letter_action, respond_to_query
from services.translate import translate_text
from telegram.constants import ParseMode
from services.transcribe import transcribe_audio
import json

from gtts import gTTS
import tempfile
import re

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_LETTER')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_sessions = {}
letter_contents = {}

ocr_cache_path = Path("ocr_cache.json")
if ocr_cache_path.exists():
    with ocr_cache_path.open("r") as f:
        try:
            ocr_cache = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("Error reading cache", str(e))
            ocr_cache = {}
                    
else:
    ocr_cache = {}

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


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def generate_audio_file(content):
    # Create a gTTS object with Chinese language
    tts = gTTS(text=content, lang='zh-CN')

    # Use a temporary file that will be automatically cleaned up
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
        temp_filename = temp_audio.name
        # Save the audio to the temporary file
        tts.save(temp_filename)
        
    print(f"Audio saved as {temp_filename}")

    return temp_filename

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_sessions[user_id] = []

    # Get the photo with the highest resolution
    photo_file = await update.message.photo[-1].get_file()
    photo_file_unique_id = photo_file.file_unique_id

    # print(photo_file)
    # photo_file_bytes = BytesIO(await photo_file.download_as_bytearray())
    
    # Acknowledge receipt of photo
    await context.bot.send_message(
        chat_id=user_id, 
        text="Processing....."
    )

    if photo_file_unique_id in ocr_cache:
        print("Using cached OCR result")
        letter_text = ocr_cache[photo_file_unique_id] 

    else:
        print(photo_file.file_path)
        letter_text = extract_content(photo_file.file_path)
        ocr_cache[photo_file_unique_id] = letter_text
        with open("ocr_cache.json", "w") as f:
            json.dump(ocr_cache, f)

    letter_contents[user_id] = letter_text

    print("Letter text", letter_text)
    
    letter_action_summary = identify_letter_action(letter_text)


    print("Letter action summary", letter_action_summary)


    letter_action_summary_translated = translate_text(letter_action_summary, target_language="zh", current_language="en")


    print("Translated letter action summary", letter_action_summary_translated)



    # Create audio file from the response
    temp_filename = generate_audio_file(letter_action_summary_translated)

    # For now, just send a placeholder response
    await context.bot.send_message(
        chat_id=user_id,
        text=letter_action_summary_translated
    )


    # Send the voice message from the temporary file
    with open(temp_filename, 'rb') as audio_file:
        await context.bot.send_voice(chat_id=user_id, voice=audio_file)
        
    # Clean up the temporary file after sending
    os.remove(temp_filename)


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
            text="Processing....."
        )
        
        # Transcribe the voice message and pass it to chatbot
        try:
            transcription_response = transcribe_audio(voice_file_bytes, f"voice_{voice_file.file_unique_id}.ogg")
            transcription_response_text = transcription_response.text
            
            # transcribe and translate to english
            transcription_response_text_translated = translate_text(transcription_response_text, target_language="en", current_language="zh")

            history.append({"role": "user", "content": transcription_response_text_translated})

            query_answer = respond_to_query(letter_text=letter_content, chat_history=history)

            # translate response back to chinese
            query_answer_translated = translate_text(query_answer, target_language="zh", current_language="en")

            history.append({"role": "assistant", "content": query_answer_translated})

            user_sessions[user_id] = history
            
            # Create audio file from the response
            temp_filename = generate_audio_file(query_answer_translated)

            await context.bot.send_message(
                chat_id=user_id,
                text=query_answer_translated,
                parse_mode=ParseMode.MARKDOWN
            )

            # Send the voice message from the temporary file
            with open(temp_filename, 'rb') as audio_file:
                await context.bot.send_voice(chat_id=user_id, voice=audio_file)
                
            # Clean up the temporary file after sending
            os.remove(temp_filename)

                    
        except Exception as e:
            logging.error(f"Error processing voice message: {str(e)}")
            await context.bot.send_message(
                chat_id=user_id,
                text="Sorry, I encountered an error processing your voice message."
            )

                

if __name__ == '__main__':
    application = ApplicationBuilder().read_timeout(30).write_timeout(30).token(TELEGRAM_TOKEN).build()
        
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
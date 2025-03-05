import logging
import os
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler
from dotenv import load_dotenv
from io import BytesIO
from services.allergen_identifier import identify_allergens

load_dotenv()

# Constants for the conversation states
ALLERGENS = 0

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_ALLERGEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_sessions = {}
user_allergens = {}

welcome_message = """
I'm here to help you find out if you are allergic to the food you want to consume.

Use the following commands if needed:
/start: Start a new conversation
/allergens: Set or update your allergen list
/clear: Clear the chat history and continue the conversation
/stop: End the conversation 
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_sessions[user_id] = []
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_chat.id] = []
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Restarting a new chat session!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Goodbye!")

async def ask_allergens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please list all your food allergens, separated by commas (e.g., peanuts, shellfish, eggs):"
    )
    return ALLERGENS

async def save_allergens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    allergens_text = update.message.text
    allergen_list = [item.strip() for item in allergens_text.split(',')]
    
    user_allergens[user_id] = allergen_list
    
    await context.bot.send_message(
        chat_id=user_id,
        text=f"Your allergens have been saved: {', '.join(allergen_list)}\nYou can update them anytime with /allergens."
    )
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':
    application = ApplicationBuilder().read_timeout(30).write_timeout(30).token(TELEGRAM_TOKEN).build()
    
    # Create conversation handler for allergens
    allergens_handler = ConversationHandler(
        entry_points=[CommandHandler('allergens', ask_allergens)],
        states={
            ALLERGENS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_allergens)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id

        if user_id in user_allergens:
            # Include the allergens in the system message or processing
            allergens = user_allergens[user_id]
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="I don't have your allergen information. Please use the /allergens command to set your allergens first."
            )
            return
        
        # Get the photo with the highest resolution
        photo_file = await update.message.photo[-1].get_file()
        print(photo_file)
        photo_file_bytes = BytesIO(await photo_file.download_as_bytearray())

        
        # Acknowledge receipt of photo
        await context.bot.send_message(
            chat_id=user_id, 
            text="I received your photo. Let me analyze it for potential allergens."
        )
        
        # Store the photo information in the user session
        identification_outcome = identify_allergens(allergens, photo_file_bytes, Path(photo_file.file_path).name)


        await context.bot.send_message(
            chat_id=user_id,
            text=identification_outcome
        )

    # Add the photo handler to the application

    start_handler = CommandHandler('start', start)
    clear_handler = CommandHandler('clear', clear)
    stop_handler = CommandHandler('stop', stop)
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(clear_handler)
    application.add_handler(stop_handler)
    application.add_handler(allergens_handler)
    application.add_handler(photo_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()
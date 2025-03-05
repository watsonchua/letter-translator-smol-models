import pyttsx3
import os
from telegram import Bot
from telegram.error import TelegramError
import asyncio
# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 150)    # Speed of speech
engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Save speech to a file
output_file = "speech.mp3"
engine.save_to_file("I will speak this text", output_file)
engine.runAndWait()

async def send_voice_message(token, chat_id, voice_file):
    """Send voice message using python-telegram-bot"""
    bot = Bot(token=token)
    try:
        with open(voice_file, 'rb') as audio:
            await bot.send_voice(chat_id=chat_id, voice=audio)
        print("Voice message sent successfully")
    except TelegramError as e:
        print(f"Error sending voice message: {e}")

# Replace with your actual token and chat_id
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# Send the voice message
if __name__ == "__main__":
    asyncio.run(send_voice_message(BOT_TOKEN, CHAT_ID, output_file))

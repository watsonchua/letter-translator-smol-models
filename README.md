# Letter Reader and Translator

## Overview

Letter Reader and Translator is a Telegram bot designed to help users who are not proficient in English, understand letters. Using the bot, all the the user has to do is to take a picture of the letter, and the app will tell them what they need to do in their native language (e.g. Chinese), in both text and voice. If the user needs more information, they can chat with the bot through voice messages in their native language.

## Features

- Scan English letters and identify action items
- Inform users of action items in their native language
- Users can ask further questions using voice messages in their native language
- Bot will reply to questions in their native language


## Deploying the Telegram bot

### Prerequisites

- Telegram bot API Key
- Jigsaw Stack API Key
- Groq API Key

Fill in `.env.sample` and save as `.env`


### Using Python
```bash
git clone https://github.com/watsonchua/letter-translator-smol-models.git
cd letter-translator-smol-models
python3 -m venv <path_to_your_env>
source path_to_your_env/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python telegram_bot/app_letter.py
```

### Using Docker
1. `docker build -t <image_name:tag> -f Dockerfile.letter .`
2. `docker run -p 8000:8000 <image_name:tag>`


## Usage

### Scanning a product

1. Go to the Telegram bot
2. Take a picture of a letter
3. Wait for the bot to identify the action items
4. Continue conversing with the bot through voice messages in your native language

Try it out:
https://t.me/letter_action_identifier_bot



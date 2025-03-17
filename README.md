# Allergen Scanner

## Overview

Allergen Scanner is a Telegram bot designed to help users identify potential allergens in food products by scanning ingredient lists. This application aims to make grocery shopping safer and easier for individuals with food allergies or dietary restrictions. It uses smol models which are less than 9B in parameter size.

## Features

- Scan product barcodes or ingredient lists
- Identify common allergens (peanuts, tree nuts, dairy, gluten, etc.)
- User-customizable allergen profiles


## Deploying the Telegram bot

### Prerequisites

- Telegram bot API Key
- Jigsaw Stack API Key
- Groq API Key

Fill in .env.sample and save as .env file


### Using Python
```bash
git clone https://github.com/watsonchua/smol-hackathon.git
cd smol-hackathon
git checkout allergen
python3 -m venv <path_to_your_env>
source path_to_your_env/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python telegram_bot/app_allergen.py
```

### Using Docker
1. `docker build -t <image_name:tag> -f Dockerfile.allergen .`
2. `docker run -p 8000:8000 <image_name:tag>`


## Usage

### Scanning a product

1. Go to the Telegram bot
2. Type /allergens to add your allergens
3. Take a picture of a food label
4. Wait for the bot to identify the allergens 


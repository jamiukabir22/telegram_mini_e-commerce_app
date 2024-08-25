from flask import Flask, request
import telegram
import os
import json
import requests

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telegram.Bot(token=TOKEN)

VENDORS_FILE = 'vendors.json'
SHOP_REQUESTS_FILE = 'shop_requests.json'

def load_vendors():
    if os.path.exists(VENDORS_FILE):
        with open(VENDORS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_vendors(vendors):
    with open(VENDORS_FILE, 'w') as file:
        json.dump(vendors, file)

def load_shop_requests():
    if os.path.exists(SHOP_REQUESTS_FILE):
        with open(SHOP_REQUESTS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_shop_requests(shop_requests):
    with open(SHOP_REQUESTS_FILE, 'w') as file:
        json.dump(shop_requests, file)

@app.route('/hook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text
    
    vendors = load_vendors()
    shop_requests = load_shop_requests()

    if message.lower().startswith('/register '):
        vendor_name = message[10:]
        if chat_id not in vendors:
            vendors[chat_id] = vendor_name
            save_vendors(vendors)
            bot.sendMessage(chat_id=chat_id, text=f"Vendor '{vendor_name}' registered successfully!")
        else:
            bot.sendMessage(chat_id=chat_id, text="You are already registered as a vendor.")
    elif message.lower() == '/shop':
        bot.sendMessage(chat_id=chat_id, text="What would you like to purchase? Please upload an image of the item.")
        shop_requests[chat_id] = {'status': 'awaiting_image'}
        save_shop_requests(shop_requests)
    else:
        if chat_id in shop_requests and shop_requests[chat_id]['status'] == 'awaiting_image':
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                new_file = bot.getFile(file_id)
                file_path = new_file.file_path
                
                shop_requests[chat_id] = {'status': 'image_received', 'file_path': file_path}
                save_shop_requests(shop_requests)
                
                bot.sendMessage(chat_id=chat_id, text="Image received! We will notify the vendors.")
                
                for vendor_chat_id in vendors.keys():
                    bot.sendPhoto(chat_id=vendor_chat_id, photo=file_path, caption="New purchase request received.")
            else:
                bot.sendMessage(chat_id=chat_id, text="Please upload an image of the item you want to purchase.")
        else:
            bot.sendMessage(chat_id=chat_id, text="Unknown command. Use /register <vendor_name> to register or /shop to shop.")
    
    return 'ok'

if __name__ == '__main__':
    app.run(port=5000)
## setting up webhook fot telegram bot ####

import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = f"https://<YOUR_DOMAIN>/hook"

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
response = requests.get(url)
print(response.json())


### combining frontend nd backend

import subprocess

@app.route('/hook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    # Call the TypeScript script to handle the command
    subprocess.run(['ts-node', 'bot.ts', message, str(chat_id)])

    return 'ok'


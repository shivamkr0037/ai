import requests
import json
from telegram.ext import Updater, MessageHandler, Filters

# Function to send a message and return the message object
def send_message(bot, chat_id, message):
    return bot.send_message(chat_id=chat_id, text=message)

# Function to edit a message with new text
def edit_message(bot, chat_id, message_id, new_text):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)

# Function to handle incoming messages from the user
def handle_message(update, context):
    url = 'https://aibr.elway-mobile.com/chatCompletion'
    user_input = update.message.text
    data = {"messages":[{"role":"user","content": user_input}]}
    headers = {
        'aibsg': 'kINH8nnVINoqkwyRuldTz0F1VwN4HrT3HP1oTgFk/u7vIUGXuq7dqSkFG2WzOahjSGHehgTOtf7bgc2RTbIdv35fVm1x9fUMD7nn+C0O++M1d/WkX+ntyjwjoyKmBU++HfmXm39EnB5eo1QfdXRAk3pFLViajSF9E3QTmMKH6rrxJB6GzpOrAUaAuqv5gQldvcBlUbP9doIN8qB+hZGt2yS9lGNK9Px4uNfclWQDQYeuHY/OCo/rInB7oxBUiziMim5KHp4LjVpneAzP7bAWT9cSEKTTI2fS10K6ohzebt6WLXXOwIdgTqpOKWuiGuMm/GLnYHHzBWxpY/5hp4e0fA==',
        'aibpf': 'android',
        'aibmd': 'default',
        'appmv': '14',
        'appvr': '1440',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Charset': 'UTF-8',
        'User-Agent': 'Ktor client',
        'Content-Type': 'text/event-stream; charset=UTF-8',
        'Content-Length': '47',
        'Host': 'aibr.elway-mobile.com',
        'Accept-Encoding': 'gzip'
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_parts = response.text.split('\n')
    previous_message = ''
    for part in response_parts:
        if part.startswith('data:{"content":"') and part.endswith('"}'):
            content = json.loads(part[5:])["content"]
            if content:
                if previous_message:
                    previous_message += ' ' + content
                    edit_message(context.bot, update.effective_chat.id, message_id, previous_message)
                else:
                    sent_message = send_message(context.bot, update.effective_chat.id, content)
                    message_id = sent_message.message_id
                    previous_message = content

# Main function to start the bot
def main():
    updater = Updater("6967792617:AAHiUcFxSDzAgnEk3HDcV5WaY_FrgZNDrRU", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

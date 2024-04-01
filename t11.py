import requests
import json
from telegram.ext import Updater, MessageHandler, Filters

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
    full_message = ""
    for part in response_parts:
        if part.startswith('data:{"content":"') and part.endswith('"}'):
            content = json.loads(part[5:])["content"]
            if content:
                full_message += content + " "
                update.message.reply_text(full_message.strip())

def main():
    updater = Updater("6967792617:AAHiUcFxSDzAgnEk3HDcV5WaY_FrgZNDrRU", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

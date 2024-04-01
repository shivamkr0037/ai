import asyncio
import requests
import uuid
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, run_async
from datetime import datetime

TOKEN = "6454261122:AAE0XvzWA4HuIYlzFECC8PbawUoV1V-fGKE"

# Dictionary mapping filter names to codes
filter_codes = {
    "Hacked Tech": 55,
    "Lyriel": 41,
    "Toonyou": 55,
    "Dyna vision": 54,
    "Elegance": 51,
    "GTA V": 45,
    "Merinaulter": 50,
    "Magical v2": 38,
    "Psychadelic": 9,
    "Psychadelic v2": 40,
    "Game art SDXL": 10,
    "Oil painting": 2,
    "Futuristic": 8,
    "Superhero": 15,
    "Blade runner": 16,
    "Comic": 23,
    "Concept painting": 27,
    "Drawing": 32,
    "Synthwave": 34,
    "Steampunk": 39,
    "Landscape": 33,
    "Insane isometric": 44,
    "Rev animated": 47,
}

# Function to make the POST request
def make_post_request(filter_name, prompt):
    url = "https://us-central1-genzart-prod.cloudfunctions.net/run_txt2image_and_store"

    headers = {
        "Host": "us-central1-genzart-prod.cloudfunctions.net",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.10.0",
    }

    new_image_uuid = str(uuid.uuid4())

    filter_code = filter_codes.get(filter_name, 55)

    data = {
        "image_uuid": new_image_uuid,
        "user_uuid": "l05AWLMt0GZMQZ1ag8NWiKCezgw2",
        "prompt": prompt,
        "num_inference_steps": 60,
        "guidance_scale": 8,
        "height": 768,
        "width": 512,
        "filter_code": filter_code,
    }

    response = requests.post(url, headers=headers, json=data)

    return new_image_uuid, response

# Function to make the GET request and save the image
def make_get_request_and_save_image(image_uuid):
    url = f"https://storage.googleapis.com/genzart-prod.appspot.com/GenZArt_results/{image_uuid}.jpg"

    headers = {
        "Host": "storage.googleapis.com",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.10.0",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(f"{image_uuid}.jpg", "wb") as f:
            f.write(response.content)
        return f"{image_uuid}.jpg"
    else:
        return None

@run_async
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! 🌟 Use /photo to choose a style. 🎨")

@run_async
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = """
    Here's how to use this bot:
    - /photo: To choose a style for generation.
    - /start: Start the bot.
    - /help: Show this help message.
    """
    update.message.reply_text(help_message)

@run_async
def photo_command(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(style, callback_data=style)] for style in filter_codes.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a style: 🎨", reply_markup=reply_markup)

@run_async
def gen_command(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    start_time = datetime.now()

    async def generate_images():
        tasks = []

        for chosen_filter, filter_code in filter_codes.items():
            tasks.append(
                asyncio.create_task(generate_image(update, chosen_filter, user_text, start_time))
            )

        await asyncio.gather(*tasks)

    asyncio.run(generate_images())

async def generate_image(update: Update, chosen_filter: str, user_text: str, start_time: datetime):
    generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                         f"📷 Image Id: Generating...\n" \
                         f"🤖 Status: Generating\n" \
                         f"⚡ Filter: {chosen_filter}\n" \
                         f"📞 Support: @randomlychats\n" \
                         f"🤵 BOT BY: 匚卄卂尺LIE"
    sent_message = update.message.reply_text(generation_message)

    new_image_uuid, post_response = make_post_request(chosen_filter, user_text)

    if post_response.status_code == 200:
        image_file = make_get_request_and_save_image(new_image_uuid)

        if image_file:
            sent_message.edit_text(f"👨‍🎤 Requested by: {update.effective_user.first_name}\n"
                                   f"📷 Image Id: {new_image_uuid}\n"
                                   "🤖 Status: Done\n"
                                   f"⚡ Filter: {chosen_filter}\n"
                                   f"⏳ Time Taken: {datetime.now() - start_time}\n"
                                   "📞 Support: @randomlychats\n"
                                   "🤵 BOT BY: 匚卄卂尺LIE")
            update.message.reply_photo(photo=open(image_file, 'rb'))
            os.remove(image_file)
        else:
            sent_message.edit_text(f"👨‍🎤 Requested by: {update.effective_user.first_name}\n"
                                   f"📷 Image Id: {new_image_uuid}\n"
                                   "🤖 Status: Failed\n"
                                   f"⚡ Filter: {chosen_filter}\n"
                                   f"⏳ Time Taken: {datetime.now() - start_time}\n"
                                   "📞 Support: @randomlychats\n"
                                   "🤵 BOT BY: 匚卄卂尺LIE\n"
                                   "Failed to retrieve the generated image.")
    else:
        update.message.reply_text(f"Failed to generate image for filter {chosen_filter}. Error: {post_response.status_code}")

@run_async
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chosen_filter = query.data
    context.user_data["chosen_filter"] = chosen_filter
    context.user_data["initiating_user"] = update.effective_user.id
    query.edit_message_text(text=f"Filter: {chosen_filter}\nPlease type your prompt.")
@run_async
def handle_user_prompt(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    
    if "chosen_filter" in context.user_data and context.user_data.get("initiating_user") == update.effective_user.id:
        chosen_filter = context.user_data["chosen_filter"]
        start_time = datetime.now()
        generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                             f"📷 Image Id: Generating...\n" \
                             f"🤖 Status: Generating\n" \
                             f"⚡ Filter: {chosen_filter}\n" \
                             f"📞 Support: @randomlychats\n" \
                             f"🤵 BOT BY: 匚卄卂尺LIE"
        sent_message = update.message.reply_text(generation_message)

        new_image_uuid, post_response = make_post_request(chosen_filter, user_text)

        if post_response.status_code == 200:
            image_file = make_get_request_and_save_image(new_image_uuid)

            if image_file:
                sent_message.edit_text(f"👨‍🎤 Requested by: {update.effective_user.first_name}\n"
                                       f"📷 Image Id: {new_image_uuid}\n"
                                       "🤖 Status: Done\n"
                                       f"⚡ Filter: {chosen_filter}\n"
                                       f"⏳ Time Taken: {datetime.now() - start_time}\n"
                                       "📞 Support: @randomlychats\n"
                                       "🤵 BOT BY: 匚卄卂尺LIE")
                update.message.reply_photo(photo=open(image_file, 'rb'))
                os.remove(image_file)
            else:
                sent_message.edit_text(f"👨‍🎤 Requested by: {update.effective_user.first_name}\n"
                                       f"📷 Image Id: {new_image_uuid}\n"
                                       "🤖 Status: Failed\n"
                                       f"⚡ Filter: {chosen_filter}\n"
                                       f"⏳ Time Taken: {datetime.now() - start_time}\n"
                                       "📞 Support: @randomlychats\n"
                                       "🤵 BOT BY: 匚卄卂尺LIE\n"
                                       "Failed to retrieve the generated image.")
        else:
            update.message.reply_text(f"Failed to generate image for filter {chosen_filter}. Error: {post_response.status_code}")
    else:
        update.message.reply_text("Invalid command. Use /photo to choose a style. 🎨")

def main():
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("photo", photo_command))
    dp.add_handler(CommandHandler("gen", gen_command))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_prompt))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

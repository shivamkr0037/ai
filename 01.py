import requests
import uuid
import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

url_text2image = "https://us-central1-genzart-prod.cloudfunctions.net/realtime_text2image"
url_image_download = "https://storage.googleapis.com/genzart-prod.appspot.com/stories/{}/{}/{}_{}.jpg"

headers = {
    "Host": "us-central1-genzart-prod.cloudfunctions.net",
    "content-type": "application/json; charset=UTF-8",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.10.0",
}

user_uuid = "uZ6eERlN0abSwRWXc60zgiXLBGs2"
call_number = 0
combined_prompt = ""

# Filter styles
styles = {
    "Magical": 3,
    "Psychadelic": 9,
    "Steampunk": 11,
    "Painting": 1,
    "Pablo Picasso": 10,
    "Game Art": 5,
    "Van Gogh": 7,
    "Anime": 13,
    "Ghibli": 8,
    "Futuristic": 12,
    "Cyberpunk": 4,
    "Photo": 14,
    "Medieval Characters": 15,
    "Superhero": 16,
    "Blade Runner": 17,
    "Cinema": 18,
    "Pixel Art": 19,
    "Unreal Engine": 20,
    "Vaporwave": 21,
    "Animation": 21,
    "3D": 22,
    "Comic": 23,
    "Charcoal": 24,
    "Mosaic": 25,
    "Artistic": 26,
    "Concept": 27,
    "Videogame": 28,
    "Watercolor": 29,
    "Concept Art": 30,
    "Digital Painting": 31,
    "Drawing": 32,
    "Landscape": 33,
    "Synthwave": 34
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to your image generation bot! Send a prompt to generate an image. Use /styles to see available styles.')

def generate_image(update: Update, context: CallbackContext) -> None:
    global user_uuid, call_number, combined_prompt

    prompt = update.message.text

    combined_prompt += f" {prompt}"

    # Extract style from message text (e.g., "/style Magical")
    style_command = "/style "
    if style_command in prompt:
        style_name = prompt.split(style_command)[1].strip()
        filter_code = styles.get(style_name)
    else:
        filter_code = 11  # Default filter code

    image_uuid = str(uuid.uuid4())
    data = {
        "image_uuid": image_uuid,
        "user_uuid": user_uuid,
        "prompt": combined_prompt.strip(),
        "height": 768,
        "width": 512,
        "filter_code": filter_code,
        "call_number": call_number,
        "seed": 3136169831,
    }

    response_generate = requests.post(url_text2image, headers=headers, json=data)

    if response_generate.status_code == 200:
        update.message.reply_text(f"Image generation successful. Image UUID: {image_uuid}")

        # Second request to save the image after generation
        response_save = requests.get(url_image_download.format(user_uuid, image_uuid, image_uuid, call_number))

        if response_save.status_code == 200:
            update.message.reply_text(f"Image save request successful.")
            update.message.reply_text(f"Saving the image from URL: {url_image_download.format(user_uuid, image_uuid, image_uuid, call_number)}")

            # Save the image in the same directory as the script
            image_filename = f"{image_uuid}_{call_number}.jpg"
            image_path = os.path.join(os.path.dirname(__file__), image_filename)

            with open(image_path, 'wb') as image_file:
                image_file.write(response_save.content)

            update.message.reply_text(f"Image saved at: {image_path}")

            # Update image_uuid for the next request
            try:
                user_uuid = response_generate.json().get("user_uuid", user_uuid)
            except json.JSONDecodeError:
                update.message.reply_text("Error decoding JSON in response. Using the previous user UUID.")

            call_number += 1
        else:
            update.message.reply_text(f"Error saving image: {response_save.status_code} - {response_save.text}")
    else:
        update.message.reply_text(f"Error generating image: {response_generate.status_code} - {response_generate.text}")

def list_styles(update: Update, context: CallbackContext) -> None:
    style_list = "\n".join(styles.keys())
    update.message.reply_text(f"Available styles:\n{style_list}")

def main() -> None:
    updater = Updater("6749956064:AAFLtmpKBXmXutUaNhZ86ooNKVeV0FuGquE")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_image))
    dispatcher.add_handler(CommandHandler("styles", list_styles))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

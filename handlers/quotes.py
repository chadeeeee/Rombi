import os
from datetime import datetime
from io import BytesIO

import pytz
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, UserProfilePhotos, BufferedInputFile

from utils.create_quote import quote

router = Router()

images_dir = "../user_images"
IMAGES_DIR = os.path.join(os.getcwd(), 'user_images')

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)


@router.message(Command('q'))
async def quotes(message: Message, command: Command, bot: Bot):
    username = f"@{message.from_user.username}"
    user_id = message.from_user.id
    date = datetime.now(pytz.timezone('Europe/Kyiv')).strftime('%d.%m.%Y')

    user_profile_photo: UserProfilePhotos = await bot.get_user_profile_photos(message.from_user.id)
    if user_profile_photo.total_count > 0:
        image = await bot.get_file(user_profile_photo.photos[0][0].file_id)
        avatar_path = f'../user_images/{user_id}.jpg'
        await bot.download_file(image.file_path, avatar_path)

        result_image = quote(command.args, username, date, user_id)

        buffer = BytesIO()
        result_image.save(buffer, format="JPEG", quality=95, optimize=True)
        buffer.seek(0)

        photo = BufferedInputFile(buffer.getvalue(), filename="quote.jpg")

        await message.answer_photo(photo=photo, caption="Ось ваша цитата")

        os.remove(avatar_path)
    else:
        await message.answer("У вас немає аватару для створення цитати.")
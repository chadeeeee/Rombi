from aiogram import Router, types, Bot
from aiogram.enums.chat_type import ChatType
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from pymongo.mongo_client import MongoClient

from config import URI

from datetime import datetime
import pytz
import os

photo_path = os.path.join(os.path.dirname(__file__), '../images/default_user_photo.jpg')

router = Router()
client = MongoClient(URI)
db = client["rombi"]
users = db["users"]
groups = db["groups"]

permissions = ("change_info+post_messages+edit_messages+delete_messages+restrict_members+invite_users+pin_messages"
               "+manage_topics+promote_members+manage_video_chats+manage_chat+post_stories+edit_stories+delete_stories")


@router.message(CommandStart())
async def start(message: Message):
    date_utc = datetime.now(pytz.UTC).strftime('%d.%m.%Y')

    user_exists = users.find_one({"user_id": message.from_user.id})

    if not user_exists:
        users.insert_one({
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
            "joined_at": date_utc
        })

    if message.chat.type == "private":
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="Додати Rombi до групи",
            url=f"t.me/RombiSfera_bot?startgroup&admin={permissions}")
        )
        builder.row(types.InlineKeyboardButton(
            text="Додати Rombi до каналу",
            url=f"t.me/RombiSfera_bot?startchannel&admin={permissions}")
        )
        await message.answer(f"👋 Привіт, <b>{message.from_user.full_name}</b>!\n"
                             f"🤖 Я Rombi - бот модератор для груп щоб адміністраторам було легше керувати групою!\n\n"
                             "➕ Добав мене в чат натиснувши кнопку <blockquote>Додати Rombi до групи</blockquote>"
                             f"або<blockquote>Додати Rombi до каналу</blockquote>\n"
                             f"🙂 Щасливого модерування!", reply_markup=builder.as_markup())
    else:
        await message.answer(f"👋 Привіт, <b>{message.from_user.full_name}</b>!\n"
                             f"🤖 Я Rombi - бот модератор для груп щоб адміністраторам було легше керувати групою!\n\n"
                             f"🙂 Щасливого модерування!")


@router.message(Command('help'))
async def help(message: Message):
    print(ChatType)
    if message.chat.type == "private":
        await message.answer("<b>📜 Меню допомоги</b>\n"
                             "/start - запуск/перезапуск бота\n"
                             "/help - викликати це меню\n"
                             "/lang - змінити мову в приватних повідоменнях з ботом (BETA)")
    elif message.chat.type != "private":
        await message.answer("<b>📜 Меню допомоги</b>\n"
                             "/start - запуск/перезапуск бота\n"
                             "/help - викликати це меню\n"
                             "/ban - заблокувати користувача в групі назавжди\n"
                             "/ro [час RO] - користувач не зможе нічого писати в чат тільки читати повідомлення\n"
                             "/q - зробити цитату [BETA]")


@router.message(Command('profile'))
async def profile(message: Message, bot: Bot):
    join_date = users.find_one({"user_id": message.from_user.id})
    print(f"join_date: {join_date['joined_at']}")
    user_id = message.from_user.id
    user_photos = await bot.get_user_profile_photos(user_id)

    if user_photos.total_count > 0:
        file_id = user_photos.photos[0][-1].file_id
        await bot.send_photo(chat_id=message.chat.id, photo=file_id,
                             caption=f"Ти <b>{message.from_user.full_name}</b>\n"
                                     f"ID: <b>{message.from_user.id}</b>\n"
                                     f"Появився: <b>{join_date} UTC</b>")
    else:
        await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(path=photo_path,
                                                                        filename="photo.jpg"),
                             caption=f"Ти <b>{message.from_user.full_name}</b>\n"
                                     f"ID: <b>{message.from_user.id}</b>\n"
                                     f"Появився: <b>{join_date} UTC</b>")


@router.message(Command("rules"))
async def show_rules(message: Message):
    group_data = groups.find_one({"group_id": message.chat.id})
    if group_data and group_data.get("rules"):
        await message.answer(f'<b>Правила групи:</b>\n{group_data["rules"]}')
        logger.info(f"Rules displayed for user {message.from_user.id} in chat {message.chat.id}")
    else:
        await message.answer("Правила групи ще не встановлені.")
        logger.info(f"User {message.from_user.id} requested rules in chat {message.chat.id}, but no rules are set.")

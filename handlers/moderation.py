from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import Message
from babel.dates import format_timedelta
from loguru import logger

from filters.bot_filters import IsChatAdmin
from utils import permissions
from utils.permissions import banned
from utils.timedelta import parse_timedelta_from_message

router = Router()


@router.message(Command('ban', prefix="!/."), IsChatAdmin())
async def ban(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.reply("<b>‼️ Команда використовується тільки в відповіді на повідомлення</b>")

    if message.reply_to_message:
        await bot.ban_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id)
        await message.answer(
            f"🚫 Користувач <b>{message.reply_to_message.from_user.first_name}</b> був заблокований назавжди!")
        logger.info(f"User banned {message.reply_to_message.from_user.first_name}")


@router.message(Command('unban', prefix="!/."), IsChatAdmin())
async def unban(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.reply("<b>‼️ Команда використовується тільки в відповіді на повідомлення</b>")

    if message.reply_to_message:
        await bot.ban_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id)
        await message.answer(
            f"✅ Користувач <b>{message.reply_to_message.from_user.first_name}</b> був розблокований!")
        logger.info(f"User unbanned {message.reply_to_message.from_user.first_name}")


@router.message(Command("ro", prefix="/!."), IsChatAdmin())
async def ro(message: types.Message):
    if not message.reply_to_message:
        await message.reply("<b>‼️ Команда використовується тільки в відповіді на повідомлення</b>")
        return

    duration = await parse_timedelta_from_message(message)
    if not duration:
        return

    try:
        await message.chat.restrict(
            message.reply_to_message.from_user.id, banned, until_date=duration
        )

        logger.info(
            "User {user} restricted by {admin} for {duration}",
            user=message.reply_to_message.from_user.id,
            admin=message.from_user.id,
            duration=duration,
        )
    except Exception as e:
        logger.error("Failed to restrict chat member: {error!r}", error=e)
        return False

    await message.reply(
        "🔇 Ви успішно заборонили писати користувачу <b>@{user}</b>, на: {duration}".format(
            user=message.reply_to_message.from_user.username,
            duration=format_timedelta(
                duration, granularity="seconds", format="short", locale="uk"
            ),
        )
    )
    logger.info(f"User {message.reply_to_message.from_user.first_name} restricted {duration}")

    return True


@router.message(Command("admin", prefix="/!."), IsChatAdmin())
async def admin(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.reply("<b>‼️ Команда використовується тільки в відповіді на повідомлення</b>")
        return
    else:
        await bot.promote_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id,
                                      **permissions.ADMIN)

        await message.answer(f"👤 <b>{message.reply_to_message.from_user.first_name}</b> тепер став адміністраторм! Вітаю!")
        logger.info(f"User {message.reply_to_message.from_user.first_name} promoted to admin")
        return


@router.message(Command("user", prefix="/!."), IsChatAdmin())
async def user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        await message.reply("<b>‼️ Команда використовується тільки в відповіді на повідомлення</b>")
        return
    else:
        await bot.promote_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id,
                                      **permissions.USER)

        await message.answer(f"👤 Нажаль, <b>{message.reply_to_message.from_user.first_name}</b> тепер звичайний користувач :(")
        logger.info(f"User {message.reply_to_message.from_user.first_name} promoted to user")
        return


@router.message(Command("kick"), IsChatAdmin())
async def kick_user(message: types.Message, bot: Bot):
    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.answer(
        f"🚷 Користувач <b>{message.reply_to_message.from_user.first_name}</b> був кікнутий з цього чату!")
    logger.info(f"User {message.reply_to_message.from_user.first_name} kicked")


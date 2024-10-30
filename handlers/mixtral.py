from utils.mixtral_chat import ai_chat
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command('ai'))
async def ask_ai(message: Message):
    answer = ai_chat(message.text)
    await message.reply(f"<b>Відповідь від AI:</b>\n{answer}")



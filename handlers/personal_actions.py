from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ChatPermissions
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

permissions = ChatPermissions(can_manage_chat=True, can_change_info=True, can_post_messages=True,
                              can_edit_messages=True, can_delete_messages=True, can_manage_video_chats=True,
                              can_invite_users=True, can_restrict_members=True, can_pin_messages=True,
                              can_manage_topics=True, can_send_messages=True, can_send_audios=True,
                              can_send_documents=True, can_send_photos=True, can_send_videos=True,
                              can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True,
                              can_send_other_messages=True, can_add_web_page_previews=True)


@router.message(CommandStart())
async def start(message: Message):
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
                         f"➕ Добав мене в чат натиснувши кнопку <blockquote>Додати Rombi до групи</blockquote>"
                         f"або<blockquote>Додати Rombi до каналу</blockquote>\n"
                         f"🙂 Щасливого модерування!", reply_markup=builder.as_markup())


import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, MEMBER, IS_NOT_MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ChatMemberUpdated, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pymongo import MongoClient

from config import URI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = Router()
client = MongoClient(URI, maxPoolSize=50, serverSelectionTimeoutMS=5000)
db = client["rombi"]
groups = db["groups"]


class ConfigureStates(StatesGroup):
    setting_hello = State()
    setting_bye = State()
    setting_rules = State()


async def check_admin_rights(user_id: int, chat_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in {'creator', 'administrator'}
    except Exception as e:
        logger.error(f"Failed to check admin rights: {e}")
        return False


def get_main_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="💬 Привітання", callback_data="set_hello"),
                types.InlineKeyboardButton(text="👋 До побачення", callback_data="set_bye"),
                types.InlineKeyboardButton(text="👮‍♂️ Правила", callback_data="set_rules"),
            ]
        ]
    )


def get_back_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Налаштувати повідомлення", callback_data="configure_message")
            ],
            [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
        ]
    )


def get_toggle_keyboard(group_data: dict, setting_type: str) -> types.InlineKeyboardMarkup:
    is_enabled = group_data.get(f"{setting_type}_enabled", True)
    status = "✅" if is_enabled else "🚫"

    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"Статус: {status}",
                    callback_data=f"toggle_{setting_type}_status"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Змінити повідомлення",
                    callback_data=f"configure_{setting_type}_message"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🔙 Повернутися до головного меню",
                    callback_data="back_to_main_menu"
                )
            ]
        ]
    )


@router.message(Command("settings"))
async def settings_command(message: Message, bot: Bot):
    try:
        if not await check_admin_rights(message.from_user.id, message.chat.id, bot):
            await message.reply("⚠️ Тільки адміністратори можуть змінювати налаштування.")
            return

        group_data = groups.find_one({"group_id": message.chat.id})
        if not group_data:
            group_data = {
                "hello": "Налаштування відсутні",
                "bye": "Налаштування відсутні",
                "rules": "Налаштування відсутні",
                "hello_enabled": True,
                "bye_enabled": True
            }

        settings_text = (
            "<b>⚙️ Поточні налаштування групи:</b>\n\n"
            "<b>👋 Привітання:</b>\n"
            f"{group_data.get('hello', 'Не встановлено')}\n\n"
            "<b>👋 Прощання:</b>\n"
            f"{group_data.get('bye', 'Не встановлено')}\n\n"
            "<b>📜 Правила:</b>\n"
            f"{group_data.get('rules', 'Не встановлено')}\n\n"
            "Оберіть, що бажаєте змінити:"
        )

        await message.reply(
            settings_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in settings_command: {e}")
        await message.reply("⚠️ Виникла помилка при отриманні налаштувань.")


@router.callback_query(F.data == "set_hello")
async def set_hello(callback_query: CallbackQuery, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        group_data = groups.find_one({"group_id": callback_query.message.chat.id})
        current_hello = group_data.get('hello',
                                       'Привітання ще не встановлено') if group_data else 'Привітання ще не встановлено'

        await callback_query.message.edit_text(
            f"<b>👋 Налаштування привітання</b>\n\n"
            f"<b>Поточне привітання:</b>\n"
            f"{current_hello}\n\n"
            f"Ви можете використовувати {'{user}'} для згадки користувача.\n"
            f"Натисніть кнопку нижче, щоб змінити привітання.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Змінити привітання", callback_data="configure_hello_message")],
                    [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню",
                                                callback_data="back_to_main_menu")]
                ]
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in set_hello: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.callback_query(F.data == "set_bye")
async def set_bye(callback_query: CallbackQuery, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        group_data = groups.find_one({"group_id": callback_query.message.chat.id})
        current_bye = group_data.get('bye',
                                     'Прощання ще не встановлено') if group_data else 'Прощання ще не встановлено'

        await callback_query.message.edit_text(
            f"<b>👋 Налаштування прощання</b>\n\n"
            f"<b>Поточне прощання:</b>\n"
            f"{current_bye}\n\n"
            f"Ви можете використовувати {'{user}'} для згадки користувача.\n"
            f"Натисніть кнопку нижче, щоб змінити прощання.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Змінити прощання", callback_data="configure_bye_message")],
                    [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню",
                                                callback_data="back_to_main_menu")]
                ]
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in set_bye: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_status(callback_query: CallbackQuery):
    setting_type = callback_query.data.split("_")[1]
    group_data = groups.find_one({"group_id": callback_query.message.chat.id})
    current_status = group_data.get(f"{setting_type}_enabled", True)
    new_status = not current_status

    groups.update_one(
        {"group_id": callback_query.message.chat.id},
        {"$set": {f"{setting_type}_enabled": new_status}},
        upsert=True
    )


@router.callback_query(F.data == "configure_hello_message")
async def configure_hello_message(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        await state.set_state(ConfigureStates.setting_hello)
        await callback_query.message.edit_text(
            "Введіть нове привітальне повідомлення:\n"
            "Використовуйте {user} для згадки користувача.\n"
            "Ви можете використовувати HTML-розмітку для форматування тексту."
        )
    except Exception as e:
        logger.error(f"Error in configure_hello_message: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.callback_query(F.data == "configure_bye_message")
async def configure_bye_message(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        await state.set_state(ConfigureStates.setting_bye)
        await callback_query.message.edit_text(
            "Введіть нове прощальне повідомлення:\n"
            "Використовуйте {user} для згадки користувача.\n"
            "Ви можете використовувати HTML-розмітку для форматування тексту."
        )
    except Exception as e:
        logger.error(f"Error in configure_bye_message: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.message(ConfigureStates.setting_hello)
async def receive_hello_message(message: Message, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(message.from_user.id, message.chat.id, bot):
            await message.reply("⚠️ Тільки адміністратори можуть змінювати налаштування.")
            await state.clear()
            return

        groups.update_one(
            {"group_id": message.chat.id},
            {"$set": {"hello": message.text}},
            upsert=True
        )

        group_data = groups.find_one({"group_id": message.chat.id})
        settings_text = (
            "<b>⚙️ Поточні налаштування групи:</b>\n\n"
            "<b>👋 Привітання:</b>\n"
            f"{group_data.get('hello', 'Не встановлено')}\n\n"
            "<b>👋 Прощання:</b>\n"
            f"{group_data.get('bye', 'Не встановлено')}\n\n"
            "<b>📜 Правила:</b>\n"
            f"{group_data.get('rules', 'Не встановлено')}\n\n"
            "Оберіть, що бажаєте змінити:"
        )

        await message.answer(
            settings_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()
    except Exception as e:
        logger.error(f"Error in receive_hello_message: {e}")
        await message.reply("⚠️ Виникла помилка при збереженні повідомлення.")
        await state.clear()


@router.message(ConfigureStates.setting_bye)
async def receive_bye_message(message: Message, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(message.from_user.id, message.chat.id, bot):
            await message.reply("⚠️ Тільки адміністратори можуть змінювати налаштування.")
            await state.clear()
            return

        groups.update_one(
            {"group_id": message.chat.id},
            {"$set": {"bye": message.text}},
            upsert=True
        )

        group_data = groups.find_one({"group_id": message.chat.id})
        settings_text = (
            "<b>⚙️ Поточні налаштування групи:</b>\n\n"
            "<b>👋 Привітання:</b>\n"
            f"{group_data.get('hello', 'Не встановлено')}\n\n"
            "<b>👋 Прощання:</b>\n"
            f"{group_data.get('bye', 'Не встановлено')}\n\n"
            "<b>📜 Правила:</b>\n"
            f"{group_data.get('rules', 'Не встановлено')}\n\n"
            "Оберіть, що бажаєте змінити:"
        )

        await message.answer(
            settings_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()
    except Exception as e:
        logger.error(f"Error in receive_bye_message: {e}")
        await message.reply("⚠️ Виникла помилка при збереженні повідомлення.")
        await state.clear()


@router.callback_query(F.data == "set_rules")
async def set_rules(callback_query: CallbackQuery, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        group_data = groups.find_one({"group_id": callback_query.message.chat.id})
        current_rules = group_data.get('rules',
                                       'Правила ще не встановлені') if group_data else 'Правила ще не встановлені'

        await callback_query.message.edit_text(
            f"<b>👮‍♂️ Налаштування правил групи</b>\n\n"
            f"<b>Поточні правила:</b>\n"
            f"{current_rules}\n\n"
            f"Натисніть кнопку нижче, щоб змінити правила.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Змінити правила", callback_data="configure_rules_message")],
                    [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню",
                                                callback_data="back_to_main_menu")]
                ]
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in set_rules: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.callback_query(F.data == "configure_rules_message")
async def configure_rules_message(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        await state.set_state(ConfigureStates.setting_rules)
        await callback_query.message.edit_text(
            "Введіть нові правила групи:\n"
            "Ви можете використовувати HTML-розмітку для форматування тексту."
        )
    except Exception as e:
        logger.error(f"Error in configure_rules_message: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.message(ConfigureStates.setting_rules)
async def receive_rules_message(message: Message, state: FSMContext, bot: Bot):
    try:
        if not await check_admin_rights(message.from_user.id, message.chat.id, bot):
            await message.reply("⚠️ Тільки адміністратори можуть змінювати налаштування.")
            await state.clear()
            return

        groups.update_one(
            {"group_id": message.chat.id},
            {"$set": {"rules": message.text}},
            upsert=True
        )

        await message.answer(
            "<b>✅ Правила групи збережено</b>",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()
    except Exception as e:
        logger.error(f"Error in receive_rules_message: {e}")
        await message.reply("⚠️ Виникла помилка при збереженні правил.")
        await state.clear()


@router.message(Command("rules"))
async def show_rules(message: Message):
    try:
        group_data = groups.find_one({"group_id": message.chat.id})
        if group_data and group_data.get("rules"):
            await message.reply(
                f"<b>📜 Правила групи:</b>\n\n{group_data['rules']}",
                parse_mode="HTML"
            )
        else:
            await message.reply("❌ Правила групи ще не встановлені.")
    except Exception as e:
        logger.error(f"Error in show_rules: {e}")
        await message.reply("⚠️ Виникла помилка при отриманні правил.")


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: CallbackQuery, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        group_data = groups.find_one({"group_id": callback_query.message.chat.id})
        if not group_data:
            group_data = {
                "hello": "Налаштування відсутні",
                "bye": "Налаштування відсутні",
                "rules": "Налаштування відсутні"
            }

        settings_text = (
            "<b>⚙️ Поточні налаштування групи:</b>\n\n"
            "<b>👋 Привітання:</b>\n"
            f"{group_data.get('hello', 'Не встановлено')}\n\n"
            "<b>👋 Прощання:</b>\n"
            f"{group_data.get('bye', 'Не встановлено')}\n\n"
            "<b>📜 Правила:</b>\n"
            f"{group_data.get('rules', 'Не встановлено')}\n\n"
            "Оберіть, що бажаєте змінити:"
        )

        await callback_query.message.edit_text(
            settings_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in back_to_main_menu: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_joined_group(event: ChatMemberUpdated, bot: Bot):
    try:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="⚙️ Налаштувати Rombi",
            callback_data=f"configure_rombi:{event.from_user.id}")
        )

        group = await bot.get_chat(event.chat.id)
        groups.update_one(
            {"group_id": group.id},
            {
                "$setOnInsert": {
                    "group_name": group.title,
                    "group_id": group.id,
                    "hello": None,
                    "rules": None,
                    "bye": None
                }
            },
            upsert=True
        )

        await bot.send_message(
            event.chat.id,
            "🥳 Привіт, я Rombi. Щоб налаштувати мене використовуйте команду /settings або натисніть кнопку <b>⚙️ Налаштувати Rombi</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in bot_joined_group: {e}")


@router.callback_query(F.data.startswith("configure_rombi"))
async def configure_rombi_callback(callback_query: CallbackQuery, bot: Bot):
    try:
        if not await check_admin_rights(callback_query.from_user.id, callback_query.message.chat.id, bot):
            await callback_query.answer("⚠️ Тільки адміністратори можуть змінювати налаштування.", show_alert=True)
            return

        group_data = groups.find_one({"group_id": callback_query.message.chat.id})
        if not group_data:
            group_data = {
                "hello": "Налаштування відсутні",
                "bye": "Налаштування відсутні",
                "rules": "Налаштування відсутні"
            }

        settings_text = (
            "<b>⚙️ Поточні налаштування групи:</b>\n\n"
            "<b>👋 Привітання:</b>\n"
            f"{group_data.get('hello', 'Не встановлено')}\n\n"
            "<b>👋 Прощання:</b>\n"
            f"{group_data.get('bye', 'Не встановлено')}\n\n"
            "<b>📜 Правила:</b>\n"
            f"{group_data.get('rules', 'Не встановлено')}\n\n"
            "Оберіть, що бажаєте змінити:"
        )

        await callback_query.message.edit_text(
            settings_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in configure_rombi_callback: {e}")
        await callback_query.answer("⚠️ Виникла помилка.", show_alert=True)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def user_joined(event: ChatMemberUpdated, bot: Bot):
    try:
        group_data = groups.find_one({"group_id": event.chat.id})
        if group_data and group_data.get("hello") and group_data.get("hello_enabled", True):
            username = event.new_chat_member.user.username or event.new_chat_member.user.full_name
            hello_message = group_data["hello"].replace("{user}", f"@{username}")
            await bot.send_message(
                event.chat.id,
                hello_message,
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Error in user_joined: {e}")


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> IS_NOT_MEMBER))
async def user_left(event: ChatMemberUpdated, bot: Bot):
    try:
        group_data = groups.find_one({"group_id": event.chat.id})
        if group_data and group_data.get("bye"):
            username = event.new_chat_member.user.username or event.new_chat_member.user.full_name
            await bot.send_message(
                event.chat.id,
                group_data["bye"].replace("{user}", f"@{username}"),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Error in user_left: {e}")

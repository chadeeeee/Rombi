from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ChatMemberUpdated, CallbackQuery, Message
import sqlite3 as sq

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, MEMBER, \
    IS_NOT_MEMBER

base = sq.connect('Rombi.db')
cur = base.cursor()

router = Router()


class ConfigureStates(StatesGroup):
    setting_hello = State()
    setting_bye = State()
    setting_rules = State()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def new_group(event: ChatMemberUpdated, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="⚙️ Налаштувати Rombi",
        callback_data=f"configure_rombi:{event.from_user.id}")
    )

    await bot.send_message(event.chat.id,
                           text="🥳 Привіт, я Rombi. Щоб налаштувати мене натисніть кнопку <blockquote>⚙️ Налаштувати Rombi</blockquote>",
                           reply_markup=builder.as_markup())
    id = str(event.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f'''
           CREATE TABLE IF NOT EXISTS {table_name} (
               chat_id TEXT PRIMARY KEY,
               hello TEXT NOT NULL,
               rules TEXT NOT NULL,
               bye TEXT NOT NULL
           )
           ''')
    cur.execute(f"INSERT OR IGNORE INTO {table_name} (chat_id, hello, rules, bye) VALUES (?, '', '', '')", (chat_id,))
    base.commit()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def user_join(event: ChatMemberUpdated, bot: Bot):
    id = str(event.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"SELECT hello FROM {table_name}")
    hello_message = cur.fetchone()
    if hello_message and hello_message[0]:
        await bot.send_message(event.chat.id, hello_message[0])


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> IS_NOT_MEMBER))
async def user_left(event: ChatMemberUpdated, bot: Bot):
    id = str(event.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"SELECT bye FROM {table_name}")
    bye_message = cur.fetchone()
    if bye_message and bye_message[0]:
        await bot.send_message(event.chat.id, bye_message[0])


@router.callback_query(F.data.startswith('configure_rombi'))
async def config_rombi(callback_query: CallbackQuery, bot: Bot):
    buttons = [
        [
            types.InlineKeyboardButton(text="💬 Привітання", callback_data="set_hello"),
            types.InlineKeyboardButton(text="👋 До побачення", callback_data="set_bye"),
            types.InlineKeyboardButton(text="👮‍♂️ Правила", callback_data="set_rules"),
        ],
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("<b>⚙️ Налаштування Rombi</b>", reply_markup=keyboard)


@router.callback_query(F.data == 'set_hello')
async def set_hello(callback_query: CallbackQuery, state: FSMContext):
    buttons = [
        [
            types.InlineKeyboardButton(text="Налаштувати повідомлення", callback_data="configure_hello_message")
        ],
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("<b>👋 Налаштування привітання</b>", reply_markup=keyboard)


@router.callback_query(F.data == 'configure_hello_message')
async def configure_hello_message(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ConfigureStates.setting_hello)
    await callback_query.message.edit_text("Введіть текст привітального повідомлення:")


@router.message(ConfigureStates.setting_hello)
async def receive_hello_message(message: Message, state: FSMContext):
    id = str(message.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"UPDATE {table_name} SET hello = ? WHERE chat_id = ?", (message.text, chat_id))
    base.commit()
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Привітальне повідомлення збережено", reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == 'set_bye')
async def set_bye(callback_query: CallbackQuery, state: FSMContext):
    buttons = [
        [
            types.InlineKeyboardButton(text="Налаштувати повідомлення", callback_data="configure_bye_message")
        ],
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("<b>👋 Налаштування до побачення</b>", reply_markup=keyboard)


@router.callback_query(F.data == 'configure_bye_message')
async def configure_bye_message(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ConfigureStates.setting_bye)
    await callback_query.message.edit_text("Введіть текст повідомлення до побачення:")


@router.message(ConfigureStates.setting_bye)
async def receive_bye_message(message: Message, state: FSMContext):
    id = str(message.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"UPDATE {table_name} SET bye = ? WHERE chat_id = ?", (message.text, chat_id))
    base.commit()
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Повідомлення до побачення збережено", reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == 'set_rules')
async def set_rules(callback_query: CallbackQuery, state: FSMContext):
    buttons = [
        [
            types.InlineKeyboardButton(text="Налаштувати правила", callback_data="configure_rules_message")
        ],
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("<b>👮‍♂️ Налаштування правил</b>", reply_markup=keyboard)


@router.callback_query(F.data == 'configure_rules_message')
async def configure_rules_message(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ConfigureStates.setting_rules)
    await callback_query.message.edit_text("Введіть текст правил:")


@router.message(ConfigureStates.setting_rules)
async def receive_rules_message(message: Message, state: FSMContext):
    id = str(message.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"UPDATE {table_name} SET rules = ? WHERE chat_id = ?", (message.text, chat_id))
    base.commit()
    buttons = [
        [types.InlineKeyboardButton(text="🔙 Повернутися до головного меню", callback_data="back_to_main_menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Правила збережено", reply_markup=keyboard)
    await state.clear()


@router.message(F.text == '/rules')
async def show_rules(message: Message):
    id = str(message.chat.id).replace("-", "")
    chat_id = f'chat_{id}'
    table_name = ''.join([c if c.isalnum() else '_' for c in chat_id])
    cur.execute(f"SELECT rules FROM {table_name}")
    rules_message = cur.fetchone()
    if rules_message and rules_message[0]:
        await message.answer(rules_message[0])


@router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu(callback_query: CallbackQuery, bot: Bot):
    await config_rombi(callback_query, bot)

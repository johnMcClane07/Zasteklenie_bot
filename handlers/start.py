from aiogram import types
from aiogram.filters.command import Command
from aiogram.dispatcher.router import Router
from keyboards.userskeyboards import main_menu_keyboard
from utils.texts import WELCOME_TEXT, WELCOME_TEXT_PHOTO
from aiogram.types import Message
from config import USERS_FILE, BOT_TOKEN
import json
from aiogram import Bot
from aiogram.fsm.context import FSMContext


bot = Bot(token=BOT_TOKEN)


router = Router()

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)  
    users = load_users()  

    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username if message.from_user.username else "None",
            "first_name": message.from_user.first_name if message.from_user.first_name else "None",
            "last_name": message.from_user.last_name if message.from_user.last_name else "None",
            'user_id': message.from_user.id,
        }
        save_users(users)  

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=WELCOME_TEXT_PHOTO,
        caption=WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(lambda c: c.data == 'main_menu')
async def main_menu(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await call.answer()
    await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=WELCOME_TEXT_PHOTO,
        caption=WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )
    






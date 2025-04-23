import asyncio
import json
import logging
from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from album_middleware import AlbumMiddleware
from config import ADMINS_ID, EXAMPLES_FILE, USERS_FILE
from keyboards.adminskeyboards import admin_panel_keyboard, save_media_keyboard, back_to_admin_panel_keyboard, faq_admin_keyboard, delete_button,faq_delete_button
from utils.texts import ADMIN_WELCOME_TEXT


router = Router()
router.message.middleware(AlbumMiddleware())

@router.message(Command("admin"))
async def cmd_start(message: Message):
    if message.from_user.id in ADMINS_ID:
        await message.answer(ADMIN_WELCOME_TEXT, reply_markup=admin_panel_keyboard())
    else:
        await message.answer("❌ У вас нет доступа к админ-панели.")

@router.callback_query(lambda c: c.data == "admin_menu")
async def admin_menu(call: types.CallbackQuery):
    if call.from_user.id in ADMINS_ID:
        await call.message.answer(ADMIN_WELCOME_TEXT, reply_markup=admin_panel_keyboard())
    else:
        await call.message.answer("❌ У вас нет доступа к админ-панели.")

class ExampleState(StatesGroup):
    waiting_for_media = State()
    waiting_for_confirmation = State()

def load_json():
    try:
        with open(EXAMPLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"media_groups": []}

def save_to_json(data):
    with open(EXAMPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class DeleteExampleState(StatesGroup):
    waiting_for_confirmation = State()

@router.callback_query(lambda c: c.data == "delete_examples")
async def delete_examples(call: types.CallbackQuery, state: FSMContext):
    examples_data = load_json()

    if not examples_data["media_groups"]:
        await call.message.answer("❌ Нет сохраненных примеров для удаления.")
        return

    for i, example in enumerate(examples_data["media_groups"]):
        media_group = []

        for photo_id in example.get("photos", []):
            media_group.append(InputMediaPhoto(media=photo_id, caption=example.get("caption", "") if len(media_group) == 0 else None))

        for video_id in example.get("videos", []):
            media_group.append(InputMediaVideo(media=video_id, caption=example.get("caption", "") if len(media_group) == 0 else None))

        if media_group:
            await call.message.answer_media_group(media=media_group)

        await call.message.answer("Удалить?", reply_markup=delete_button(i))

    await call.message.answer('Вернуться в главное меню', reply_markup=back_to_admin_panel_keyboard())

    await state.set_state(DeleteExampleState.waiting_for_confirmation)

@router.callback_query(lambda c: c.data.startswith("delete_example_"))
async def confirm_delete_example(call: types.CallbackQuery, state: FSMContext):
    index = int(call.data.split("_")[-1])
    examples_data = load_json()

    if 0 <= index < len(examples_data["media_groups"]):
        del examples_data["media_groups"][index]
        save_to_json(examples_data)
        await call.message.answer("✅ Пример успешно удален!")
        await delete_examples(call, state)
    else:
        await call.message.answer("❌ Ошибка: пример не найден.")

@router.callback_query(lambda c: c.data == "add_examples")
async def add_examples(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📸 Отправьте одно или несколько изображений/видео (максимум 5).")
    await state.set_state(ExampleState.waiting_for_media)
    await call.answer()

@router.message(ExampleState.waiting_for_media, F.photo | F.video)
async def process_media(message: types.Message, state: FSMContext, album: list = None):
    new_group = {"photos": [], "videos": [], "caption": message.caption.strip() if message.caption else ""}
    logging.info(album)

    if album:  
        for msg in album:
            if msg.photo:
                largest_photo = max(msg.photo, key=lambda photo: photo.file_size)
                new_group["photos"].append(largest_photo.file_id)
            if msg.video:
                new_group["videos"].append(msg.video.file_id)
            if msg.caption:
                new_group["caption"] = msg.caption
    else:  
        if message.photo:
            new_group["photos"].append(message.photo[-1].file_id)
        if message.video:
            new_group["videos"].append(message.video.file_id)

    media_group = MediaGroupBuilder(caption=new_group["caption"])
    
    for photo in new_group["photos"]:
        media_group.add_photo(media=photo)
    for video in new_group["videos"]:
        media_group.add_video(media=video)

    if new_group["photos"] or new_group["videos"]:
        if len(new_group["photos"]) + len(new_group["videos"]) > 1:
            await message.answer_media_group(media=media_group.build())  
        else:
            if new_group["photos"]:
                media = InputMediaPhoto(media=new_group["photos"][0], caption=new_group["caption"])
                await message.answer_media_group([media])
            elif new_group["videos"]:
                media = InputMediaVideo(media=new_group["videos"][0], caption=new_group["caption"])
                await message.answer_media_group([media])

        await message.answer(text="Вы хотите сохранить этот контент?", reply_markup=save_media_keyboard())
        await state.update_data(new_group=new_group)
        await state.set_state(ExampleState.waiting_for_confirmation)


@router.callback_query(lambda c: c.data == "save_media")
async def save_media(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    new_group = user_data.get("new_group")

    if not new_group:
        await call.message.answer("❌ Ошибка: контент не найден!")
        return

    existing_data = load_json()
    existing_data["media_groups"].append(new_group)
    save_to_json(existing_data)

    await call.message.answer("✅ Контент успешно сохранен!")
    await state.clear()

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

async def get_all_users():
    users = load_users()
    return list(users.keys())

class BroadcastState(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_confirmation = State()

@router.callback_query(F.data == "send_broadcast")
async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст рассылки:")
    await state.set_state(BroadcastState.waiting_for_text)
    await callback.answer()

@router.message(BroadcastState.waiting_for_text, F.text)
async def get_message_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Хотите прикрепить фото или видео? Отправьте медиа или напишите 'нет'.")
    await state.set_state(BroadcastState.waiting_for_media)

@router.message(BroadcastState.waiting_for_media, F.photo | F.video | F.text)
async def get_media_and_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    media = None

    if message.text:  
        if message.text.lower() == "нет":
            await message.answer(f"Вы уверены, что хотите отправить рассылку с текстом:\n\n{text}\n\nНажмите 'Подтвердить' или 'Отменить'.",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_broadcast"),
                                      InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
                                 ]))
            await state.set_state(BroadcastState.waiting_for_confirmation)
        else:
            if message.photo:
                media = InputMediaPhoto(media=message.photo[-1].file_id, caption=text)
            elif message.video:
                media = InputMediaVideo(media=message.video.file_id, caption=text)

            await state.update_data(media=media)

            await message.answer("Вы уверены, что хотите отправить рассылку?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_broadcast"),
                 InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
            ]))

    else:
        if message.photo:
            media = InputMediaPhoto(media=message.photo[-1].file_id, caption=text)
        elif message.video:
            media = InputMediaVideo(media=message.video.file_id, caption=text)

        await state.update_data(media=media)

        await message.answer("Вы уверены, что хотите отправить рассылку?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_broadcast"),
             InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
        ]))

    await state.set_state(BroadcastState.waiting_for_confirmation)

@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    media = data.get("media", None)

    users = await get_all_users()
    if not users:
        await callback.message.answer("Нет подписчиков для рассылки.")
        await state.clear()
        return

    sent_count = 0
    for user_id in users:
        try:
            if media:
                await callback.bot.send_media_group(chat_id=int(user_id), media=[media])
            else:
                await callback.bot.send_message(chat_id=int(user_id), text=text)

            sent_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(f"Ошибка при отправке пользователю {user_id}: {e}")

    await callback.message.answer(f"✅ Сообщение отправлено {sent_count} подписчикам!",reply_markup=back_to_admin_panel_keyboard())
    await state.clear()

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Рассылка отменена.",reply_markup=back_to_admin_panel_keyboard())
    await state.clear()



def load_faq_data():
    try:
        with open("faq_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохранение данных в JSON
def save_faq_data(faq_data):
    with open("faq_data.json", "w", encoding="utf-8") as file:
        json.dump(faq_data, file, ensure_ascii=False, indent=4)

FAQ_DATA = load_faq_data()

# Состояния для добавления вопроса
class FAQStates(StatesGroup):
    waiting_for_question = State()  # Ожидаем вопрос
    waiting_for_answer = State()    # Ожидаем ответ

# Колбек для кнопки управления FAQ
@router.callback_query(lambda c: c.data == "manage_faq")
async def manage_faq(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("❓ <b>Введите новый вопрос для FAQ:</b>")
    await call.message.answer("Введите новый вопрос для FAQ.")
    await call.answer()
    await state.set_state(FAQStates.waiting_for_question)

# Состояние для получения вопроса
@router.message(FAQStates.waiting_for_question)
async def get_question(message: types.Message, state: FSMContext):
    question = message.text
    await state.update_data(question=question)
    await message.answer("✅ Вопрос получен! Теперь отправьте ответ на него.")
    await state.set_state(FAQStates.waiting_for_answer)

# Состояние для получения ответа
@router.message(FAQStates.waiting_for_answer)
async def get_answer(message: types.Message, state: FSMContext):
    answer = message.text
    user_data = await state.get_data()
    question = user_data.get("question")

    # Обновляем данные с ответом
    FAQ_DATA[question] = [question, answer]  # Теперь это список: [вопрос, ответ]

    # Сохраняем данные в JSON
    save_faq_data(FAQ_DATA)

    # Отправляем уведомление о успешном добавлении
    await message.answer(f"✅ Новый вопрос и ответ успешно добавлены в FAQ!\n\n<b>Вопрос:</b> {question}\n<b>Ответ:</b> {answer}")
    await state.clear()

    # Возвращаем пользователя в меню FAQ
    await message.answer("Возвращаемся к FAQ.", reply_markup=faq_admin_keyboard())

class DeleteFAQState(StatesGroup):
    waiting_for_confirmation = State()

@router.callback_query(lambda c: c.data == "delete_faq")
async def show_faq_for_deletion(call: types.CallbackQuery, state: FSMContext):
    faq_data = load_faq_data()

    if not faq_data:
        await call.message.answer("❌ Вопросов в FAQ нет.")
        return

    for question, answer in faq_data.items():
        await call.message.answer(
            f"❓ <b>{question}</b>\n\n💡 {answer}",
            parse_mode="HTML",
            reply_markup=faq_delete_button(question)
        )
    await call.message.answer('Вернуться в главное меню', reply_markup=back_to_admin_panel_keyboard())  
    await state.set_state(DeleteFAQState.waiting_for_confirmation)

@router.callback_query(lambda c: c.data.startswith("delete_faq_"))
async def delete_faq(call: types.CallbackQuery, state: FSMContext):
    question = call.data.replace("delete_faq_", "")
    faq_data = load_faq_data()

    if question in faq_data:
        del faq_data[question]
        save_faq_data(faq_data)
        await call.message.answer("✅ Вопрос удален!")

        await show_faq_for_deletion(call, state)
    else:
        await call.message.answer("❌ Ошибка: вопрос не найден.")


STATS_FILE = "stats.json"

def load_stats():
    """Загрузка статистики из JSON"""
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users_count": 0, "messages_count": 0}

def save_stats(stats):
    """Сохранение статистики в JSON"""
    with open(STATS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4, ensure_ascii=False)

def update_message_count():
    """Увеличение счетчика сообщений"""
    stats = load_stats()
    stats["messages_count"] += 1
    save_stats(stats)

def get_users_count():
    """Получение количества пользователей"""
    users = load_users()
    return len(users)  

@router.message()
async def count_messages(message: Message):
    """Обновляем статистику сообщений"""
    update_message_count()

@router.callback_query(lambda call: call.data == "bot_statistics")
async def bot_statistics_callback(call: CallbackQuery):
    """Вывод статистики по кнопке из меню"""
    stats = load_stats()
    users_count = get_users_count() 

    response = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Количество пользователей: {users_count}\n"
        f"💬 Сообщений обработано: {stats['messages_count']}"
    )
    await call.message.edit_text(response, parse_mode="HTML")
from config import ADMIN_CHAT_ID, BOT_TOKEN
from keyboards.userskeyboards import back_to_menu
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Bot
import re
from amocrm.v2 import Lead as _Lead, Contact
import logging
from amocrm.v2.entity.custom_field import ContactPhoneField, TextCustomField

bot = Bot(token=BOT_TOKEN)
router = Router()

def validate_phone_number(phone: str):
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not re.match(r"^\+?\d+$", phone):
        return None
    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]
    elif phone.startswith("+7") and len(phone) == 12:
        pass  
    else:
        return None
    return phone

async def send_application_to_admin(application_data):
    try:
        message = (
            f"<b>✨ Новая заявка ✨</b>\n\n"
            f"<b>📌 Имя:</b> {application_data['name']}\n"
            f"<b>📞 Телефон:</b> {application_data['phone']}\n"
            f"<b>💬 Сообщение:</b> {application_data['message']}"
        )
        await bot.send_message(ADMIN_CHAT_ID, message, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка при отправке заявки админу: {e}")

'''class Lead(_Lead):
    phone = ContactPhoneField('PHONE', enum='WORK', required=True)

async def send_application_to_amocrm(application_data):
    payload = {
        "name": application_data['name'],
        "custom_fields_values": [
            {
                "field_code": "PHONE",
                "values": [
                    {"value": application_data['phone'], "enum": "WORK"}
                ]
            }
        ]
    }

    # Логируем тип аргументов перед create
    logging.debug("Payload type: %s, payload: %r", type(payload), payload)

    try:
        # Передаём СЛОВАРЬ напрямую, без обёртки в список
        created = await Lead.create(payload)
        return {"status": "success", "data": created}
    except Exception as e:
        resp = getattr(e, 'response', None)
        err_body = resp.json() if resp else str(e)
        logging.error("AmoCRM error: %s", err_body)
        return {"status": "error", "message": err_body}'''
        

class ApplicationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_message = State()

@router.callback_query(lambda c: c.data == "apply")
async def leave_application(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("<b>✨ Пожалуйста, напишите ваше имя ✨</b>", parse_mode="HTML")
    await state.set_state(ApplicationState.waiting_for_name)
    await call.answer()

@router.message(ApplicationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip()
    if not user_name:
        await message.answer("<b>❌ Имя не может быть пустым. Пожалуйста, введите ваше имя.</b>", parse_mode="HTML")
        return
    await state.update_data(name=user_name)
    await message.answer("<b>✨ Теперь, пожалуйста, введите ваш номер телефона ✨</b>", parse_mode="HTML")
    await state.set_state(ApplicationState.waiting_for_phone)

@router.message(ApplicationState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_phone = validate_phone_number(message.text.strip())
    if not user_phone:
        await message.answer("<b>❌ Неверный формат телефона. Пожалуйста, введите ваш номер телефона.</b>", parse_mode="HTML")
        return
    await state.update_data(phone=user_phone)
    await message.answer("<b>✨ Если у вас есть дополнительное сообщение, введите его, или просто отправьте 'Нет'. ✨</b>", parse_mode="HTML")
    await state.set_state(ApplicationState.waiting_for_message)

@router.message(ApplicationState.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text.strip()
    if user_message.lower() == "нет":
        user_message = "Нет дополнительного сообщения"
    await state.update_data(message=user_message)
    user_data = await state.get_data()

    final_message = (
        f"<b>✨ Ваша заявка:</b>\n\n"
        f"<b>📌 Имя:</b> {user_data['name']}\n"
        f"<b>📞 Телефон:</b> {user_data['phone']}\n"
        f"<b>💬 Сообщение:</b> {user_data['message']}"
    )
    await message.answer(final_message, parse_mode="HTML")
    await message.answer("<b>✅ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.</b>", parse_mode="HTML", reply_markup=back_to_menu())
    await send_application_to_admin(user_data)
    #await send_application_to_amocrm(user_data)


    await state.clear()

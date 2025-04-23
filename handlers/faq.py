import json
from aiogram import Router, types
from keyboards.userskeyboards import faq_keyboard, back_to_faq_keyboard
from aiogram.fsm.context import FSMContext

router = Router()

def load_faq_data():
    try:
        with open("faq_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


@router.callback_query(lambda c: c.data == "faq")
async def show_faq(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❓ <b>Выберите вопрос:</b>", reply_markup=faq_keyboard(), parse_mode="HTML")
    await call.answer()

@router.callback_query(lambda c: c.data.startswith("faq_"))
async def faq_answer(call: types.CallbackQuery):
    FAQ_DATA = load_faq_data()
    question_key = call.data.split("_")[1]
    if question_key in FAQ_DATA:
        question, answer = FAQ_DATA[question_key]
        message_text = f"❓ <b>{question}</b>\n\n{answer}"
        await call.message.edit_text(message_text, reply_markup=back_to_faq_keyboard(), parse_mode="HTML")
    await call.answer()


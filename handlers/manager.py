from aiogram import Router, types
from keyboards.userskeyboards import contact_manager_keyboard
from config import MANAGER_PHONE_NUMBER
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(lambda c: c.data == "contact_manager")
async def contact_manager(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    message_text = (
        "📞 <b>Связаться с менеджером</b>\n\n"
        "Вы можете связаться с нашим менеджером по следующим контактам:\n"
        f"📍 <b>Телефон:</b> {MANAGER_PHONE_NUMBER}\n"
    )

    await call.message.answer(message_text, reply_markup=contact_manager_keyboard(), parse_mode="HTML")
    await call.answer()


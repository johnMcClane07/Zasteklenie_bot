from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from keyboards.userskeyboards import pagination_keyboard, choose_complection_keyboard, choose_extras_keyboard, clear_extras_keyboard,back_to_main_menu
from aiogram import F
import re
from aiogram.fsm.context import FSMContext
from aiogram import exceptions
import logging
from prices import DATA, COMPLECTION_PRICES, COMPLECTIONS, ADDITIONAL_SERVICES, EXTRA_PRICES, BASE_PRICE_PER_M2

router = Router()

class CalculatorState(StatesGroup):
    waiting_for_type = State()
    waiting_for_size = State()
    waiting_for_complectation = State()
    waiting_for_extras = State()


@router.callback_query(lambda c: c.data == 'calculate')
async def calculate(call, state):
    first_item = DATA[0]

    await call.message.answer("✨ <b>Выберите тип стеклопакета</b> ✨\n\n", parse_mode="HTML")

    await call.message.answer_photo(
        photo=first_item["file_id"], 
        caption=f"<b>{first_item['name']}</b>",  # Сделаем название жирным
        reply_markup=pagination_keyboard(1),
        parse_mode="HTML"
    )

    await state.set_state(CalculatorState.waiting_for_type)
    await call.answer()


@router.callback_query(F.data.startswith("page_"))
async def change_page(call: types.CallbackQuery, state: State):
    page = int(call.data.split("_")[1])  
    
    if 1 <= page <= len(DATA):
        data = DATA[page - 1] 
        await call.message.edit_media(
            media=types.InputMediaPhoto(media=data["file_id"], caption=f"<b>{data['name']}</b>", text="✨ <b>Выберите тип стеклопакета</b> ✨\n\n", parse_mode="HTML"),
            reply_markup=pagination_keyboard(page),
            parse_mode="HTML"
        )

    await call.answer()


@router.callback_query(F.data.startswith("select_type"))
async def select_window(call: types.CallbackQuery, state: State):
    page = int(call.data.split("_")[2]) 
    data = DATA[page - 1] 

    await state.update_data(window_type=data['name'])

    await state.set_state(CalculatorState.waiting_for_size)
    await call.message.answer("✨ <b>Введите размер окна в формате: ширина x высота</b> ✨\nПример: <code>1200x800</code>", parse_mode="HTML")

    await call.answer()


@router.message(CalculatorState.waiting_for_size)
async def calculate_size(message, state):
    user_input = message.text.strip()

    if re.match(r'^\d+[xх]\d+$', user_input, re.IGNORECASE):
        await state.update_data(window_size=user_input) 

        await message.answer("✨ <b>Выберите комплектацию</b> ✨\n\n", parse_mode="HTML")

        await state.set_state(CalculatorState.waiting_for_complectation)

        for i, complection in enumerate(COMPLECTIONS):
            text = f"💥 <b>{complection['name']}</b> 💥\n\n{complection['description']}"
            
            await message.answer(
                text,
                reply_markup=choose_complection_keyboard(i),
                parse_mode="HTML"
            )
    else:
        await message.answer("❌ Неверный формат! Пожалуйста, введите размер в формате: <code>ширина x высота</code> (например, <code>100x150</code>).", parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("select_complection_"))
async def select_complection(call: types.CallbackQuery, state: FSMContext):
    complection_index = int(call.data.split("_")[-1])  
    selected_complection = COMPLECTIONS[complection_index]
    
    await state.update_data(selected_complection=selected_complection)

    await call.message.answer(f"🛒 Вы выбрали комплектацию: <b>{selected_complection['name']}</b>.", parse_mode="HTML")
    await call.answer()

    extras_msg = await call.message.answer(
        "✨ <b>Выберите дополнительные услуги:</b>",
        reply_markup=choose_extras_keyboard(),
        parse_mode="HTML"
    )

    selected_extras_msg = await call.message.answer("🛒 <b>Выбранные услуги:</b>\n(пока пусто)", parse_mode="HTML")

    await state.update_data(
        extras_message_id=extras_msg.message_id,
        selected_extras_message_id=selected_extras_msg.message_id,
        selected_extras=[],  
        last_selected_extras_text="🛒 <b>Выбранные услуги:</b>\n(пока пусто)"
    )

    await state.set_state("waiting_for_extras")


@router.callback_query(lambda c: c.data.startswith("select_extra_"))
async def select_extra(call: types.CallbackQuery, state: FSMContext):
    extra_index = call.data.split("_")[-1]
    extra = ADDITIONAL_SERVICES[int(extra_index)]['name']
    logging.info(f"Выбрана услуга: {extra}")

    user_data = await state.get_data()
    selected_extras = user_data.get("selected_extras", [])

    if extra not in selected_extras:
        selected_extras.append(extra)
        await state.update_data(selected_extras=selected_extras)

    new_extras_text = "🛒 <b>Выбранные услуги:</b>\n" + "\n".join([f"• {e}" for e in selected_extras])

    selected_extras_msg_id = user_data.get("selected_extras_message_id")
    last_sent_text = user_data.get("last_selected_extras_text", "")

    if selected_extras_msg_id and new_extras_text != last_sent_text:
        try:
            await call.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=selected_extras_msg_id,
                text=new_extras_text,
                parse_mode="HTML",
                reply_markup=clear_extras_keyboard()
            )

            await state.update_data(last_selected_extras_text=new_extras_text)
        except exceptions.TelegramBadRequest:
            pass  

    await call.answer("Добавлено!")


@router.callback_query(lambda c: c.data == "clear_extras")
async def clear_extras(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(selected_extras=[], last_selected_extras_text="✅ <b>Выбранные услуги:</b>\n(пока пусто)", reply_markup=choose_extras_keyboard())
    await call.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="✅ <b>Выбранные услуги:</b>\n(пока пусто)",
        parse_mode="HTML",
        reply_markup=clear_extras_keyboard()
    )
    await call.answer("Услуги очищены!")


@router.callback_query(lambda c: c.data == "count_cost")
async def calculate_price(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    window_type = user_data.get("window_type")
    window_size = user_data.get("window_size")
    selected_complection = user_data.get("selected_complection", {})
    selected_extras = user_data.get("selected_extras", [])

    if not window_type or not window_size or not selected_complection:
        await call.message.answer("❌ Данные для расчета неполные! Проверьте ввод.", parse_mode="HTML")
        logging.error("Ошибка: отсутствуют данные для расчета!")
        return

    window_size = window_size.lower().replace("х", "x")  # заменяем русскую "х" на английскую "x"
    width, height = map(int, window_size.split("x"))

    area_m2 = (width / 1000) * (height / 1000)  

    base_price_per_m2 = BASE_PRICE_PER_M2.get(window_type, 0)
    base_cost = area_m2 * base_price_per_m2


    complection_cost = COMPLECTION_PRICES.get(selected_complection["code"], 0)

    extra_cost = sum(EXTRA_PRICES.get(extra["code"], 0) for extra in ADDITIONAL_SERVICES if extra["name"] in selected_extras)

    total_price = base_cost + complection_cost + extra_cost

    price_message = (
        f"✨ <b>Расчет стоимости</b> ✨\n\n"
        f"📌 <b>Тип окна:</b> {window_type}\n"
        f"📏 <b>Размер:</b> {window_size} мм\n"
        f"🏗 <b>Комплектация:</b> {selected_complection['name']}\n"
        f"🛠 <b>Доп. услуги:</b> {', '.join(selected_extras) if selected_extras else 'Нет'}\n"
        f"💰 <b>Итоговая цена:</b> {total_price:.2f} ₽"
    )

    await call.message.answer(price_message, reply_markup=back_to_main_menu(), parse_mode="HTML")
    await state.clear()
    await call.answer()

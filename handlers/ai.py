from openai import AsyncOpenAI
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx
from config import PROXY, SYSTEM_PROMPT, OPENAI_KEY

router=Router()


transport = httpx.AsyncHTTPTransport(proxy=PROXY, local_address="0.0.0.0")
http_client = httpx.AsyncClient(transport=transport)

client = AsyncOpenAI(
    api_key=OPENAI_KEY,
    http_client=http_client
)


async def ask_ai(user_message):
    print(f"[DEBUG] Отправка запроса: {user_message}")
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        print(f"[DEBUG] Ответ от OpenAI: {response}")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return "Извините, произошла ошибка при обращении к ИИ. Попробуйте позже."

class ChatGPT(StatesGroup):
    waiting_for_message = State()

@router.callback_query(lambda c: c.data == "chat_with_ai")
async def chat_with_ai(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ChatGPT.waiting_for_message)

    await call.message.answer("✨ Пожалуйста, напишите ваш вопрос ✨")
    await call.answer()

@router.message(ChatGPT.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text.strip()
    if not user_message:
        await message.answer("<b>❌ Вопрос не может быть пустым. Пожалуйста, напишите ваш вопрос.</b>", parse_mode="HTML")
        return
    
    await message.answer("⌛ Пожалуйста, подождите. ИИ думает...")

    ai_response = await ask_ai(user_message)
    await message.answer(f"<b>✨ ИИ-помощник ответил:</b>\n\n{ai_response}", parse_mode="HTML")

    await state.clear()



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from prices import ADDITIONAL_SERVICES
from config import MANAGER_TELEGRAM_USERNAME
from handlers.admin import load_faq_data
from prices import DATA


def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Рассчитать стоимость", callback_data="calculate")],
        [InlineKeyboardButton(text="🖼 Показать примеры работ", callback_data="examples")],
        [InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq")],
        [InlineKeyboardButton(text="📩 Оставить заявку", callback_data="apply")],
        [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="contact_manager")],
        [InlineKeyboardButton(text="🤖 Написать ИИ-помощнику", callback_data="chat_with_ai")]
    ])


def pagination_keyboard(page: int):
    TOTAL_PAGES = len(DATA)
    buttons = [
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"page_{page-1}") if page > 1 else InlineKeyboardButton(text=" ", callback_data="none"),
            InlineKeyboardButton(text=f"{page}/{TOTAL_PAGES}", callback_data="none"),
            InlineKeyboardButton(text="➡️", callback_data=f"page_{page+1}") if page < TOTAL_PAGES else InlineKeyboardButton(text=" ", callback_data="none")
        ],
        [
            InlineKeyboardButton(text="✅ Выбрать", callback_data=f"select_type_{page}") 
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def choose_complection_keyboard(i: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выбрать", callback_data=f"select_complection_{i}")]
        ]
    )

def choose_extras_keyboard():
    inline_keyboard = []
    
    for extra in ADDITIONAL_SERVICES:
        button = InlineKeyboardButton(text=extra["name"], callback_data=f"select_extra_{extra['index']}")
        inline_keyboard.append([button])  

    inline_keyboard.append([InlineKeyboardButton(text="❌ Рассчитать без доп. услуг", callback_data="count_cost")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    return keyboard


def clear_extras_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧹 Очистить", callback_data="clear_extras")],
        [InlineKeyboardButton(text="📊 Рассчитать стоимость", callback_data="count_cost")]

        
    ])

def back_to_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать стоимость заново", callback_data="calculate")],
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")]
    ])

def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")]
    ])

def contact_manager_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать в Telegram", url=f"https://t.me/{MANAGER_TELEGRAM_USERNAME}")],
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="main_menu")]
    ])


def faq_keyboard():
    FAQ_DATA = load_faq_data()
    inline_keyboard = []

    for key, value in FAQ_DATA.items():
        question = value[0] 
        button = InlineKeyboardButton(text=question, callback_data=f"faq_{key}")
        inline_keyboard.append([button]) 

    back_button = InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")
    inline_keyboard.append([back_button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return keyboard

def back_to_faq_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="faq")]
    ])






from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Добавить примеры работ", callback_data="add_examples")],
        [InlineKeyboardButton(text="🖼 Удалить примеры работ", callback_data="delete_examples")],
        [InlineKeyboardButton(text="📢 Отправить рассылку", callback_data="send_broadcast")],
        [InlineKeyboardButton(text="❓ Часто задаваемые вопросы", callback_data="manage_faq")],
        [InlineKeyboardButton(text="❓ Удалить Часто задаваемые вопросы", callback_data="delete_faq")],
        [InlineKeyboardButton(text="📊 Статистика бота", callback_data="bot_statistics")],
        
    ])

def save_media_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сохранить", callback_data="save_media")],
        [InlineKeyboardButton(text="🔄 Переделать", callback_data="add_examples")]
    ])
def back_to_admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Вернуться в панель администратора", callback_data="admin_menu")]
    ])

def faq_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить новый вопрос", callback_data="manage_faq")],
        [InlineKeyboardButton(text="Просмотр FAQ", callback_data="view_faq")]
    ])
    return keyboard

def delete_button(index):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_example_{index}")],
        ]
    )

def faq_delete_button(question):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_faq_{question}")],
        ]
    )

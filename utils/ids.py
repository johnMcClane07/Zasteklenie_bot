"""@router.message(lambda message: message.photo)
async def get_photo_id(message: Message):
    file_id = message.photo[-1].file_id  
    await message.answer(f"📸 File ID:\n`{file_id}`", parse_mode="Markdown")

@router.message(lambda message: message.chat.type in ["group", "supergroup"])
async def get_group_chat_id(message: types.Message):
    group_chat_id = message.chat.id
    await message.answer(f"Chat ID этой группы: {group_chat_id}")"""
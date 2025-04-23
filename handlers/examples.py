from aiogram import Router
from aiogram import types
from handlers.admin import load_json
from aiogram.utils.media_group import MediaGroupBuilder
import logging
import asyncio
from keyboards.userskeyboards import back_to_menu
from aiogram.fsm.context import FSMContext


router = Router()

@router.callback_query(lambda c: c.data == 'examples')
async def examples(call: types.CallbackQuery,state: FSMContext):
    await state.clear()
    media_groups = load_json()["media_groups"]

    for new_group in media_groups:
        media_group = MediaGroupBuilder(caption=new_group["caption"])

        if new_group["photos"]:
            for photo in new_group["photos"]:
                media_group.add_photo(media=photo)  
        if new_group["videos"]:
            for video in new_group["videos"]:
                media_group.add_video(media=video)

        await call.message.answer_media_group(media=media_group.build())
        await call.answer()
        await asyncio.sleep(1)

    await call.answer()
    await call.message.answer("👀 Вот несколько примеров наших работ!", reply_markup=back_to_menu())
    


   
    

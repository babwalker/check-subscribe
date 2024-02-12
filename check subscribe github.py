import sys
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging

channel_text = """
Подпишись на эти каналы
Когда подпишешься нажми на кнопку
"""

CHANNELS = []

keyboards = [[InlineKeyboardButton(text = "Я подписался", callback_data="check")]]
keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboards)

router = Router()
bot = Bot(token="token")

async def check_sub_channels(user_id):
    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if isinstance(chat_member, ChatMemberLeft):
            return False
    return True

@router.chat_join_request()
async def approve_request_router(chat_join_request: types.ChatJoinRequest):
    if await check_sub_channels(chat_join_request.from_user.id):
        await chat_join_request.approve()
    else:
        await bot.send_message(text=channel_text, chat_id=chat_join_request.from_user.id, reply_markup=keyboard_markup)    
    
async def approve_request(user_id):
    if await check_sub_channels(user_id):
        await bot.approve_chat_join_request(chat_id="chat_id", user_id=user_id)
    else:
        await bot.send_message(text=channel_text, chat_id=user_id, reply_markup=keyboard_markup)
    
@router.message(Command("start"))
async def test_start(message: types.Message):
    if await check_sub_channels(message.from_user.id):
        await message.answer("Получилось")
    else:
        await message.answer("Не получилось")

@router.callback_query(F.data == "check")
async def send_message(callback: types.CallbackQuery):
    await approve_request(callback.from_user.id)

async def main():

    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
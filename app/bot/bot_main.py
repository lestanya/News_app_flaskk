

import asyncio
import sys
import os
import logging


from aiogram import Bot, Dispatcher, html
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from dotenv import load_dotenv, find_dotenv
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

def load_token():
    load_dotenv(find_dotenv())
    TOKEN = os.getenv('TOKEN')
    return TOKEN

dp = Dispatcher()

user_router = Router()

dp.include_router(user_router)


async def main():
    bot = Bot(
        token=load_token(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    return bot


@user_router.message(CommandStart())
async def command_start(message: Message):
    await message.answer('Привет!\n ' \
    'Я Бот технической поддержки\n' \
    'Напиши здесь что бы ты хотел улучшить в сайте или жалобу')
    await message.answer('https://docs.google.com/forms/d/e/1FAIpQLSe2eNjCYwfufZ0BVCuazoHrmaRjrDwPxXJ_3cSxl2djHRSvSQ/viewform?usp=header')    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
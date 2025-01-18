
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message


bot = Bot(token='8135204327:AAFfOpBtImS1UEO71AFuEg4penaSB9RU8kM')
dp = Dispatcher()


@dp.message()
async def cmd_start(message: Message):
    await message.answer('Привет!')
    await message.reply('Как дела?')


async def main():
    await dp.start_polling(bot)


if name == 'main':
    asyncio.run(main())

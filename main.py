import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


bot = Bot()
dp = Dispatcher()


@dp.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer('Привет!')
    await message.reply('Как дела?')


async def main():
    await dp.start_polling(bot)


if name == 'main':
    asyncio.run(main())
    except KeyboardInterrupt:
    print('Бот выключен')

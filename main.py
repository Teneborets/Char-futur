import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import feedparser
import asyncio

logging.basicConfig(level=logging.INFO)

API_TOKEN = '8106970514:AAHzqTa-wKim6XauPoSiiVTm89Ic1h9QXBg'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

RSS_FEEDS = {
    "Lenta.ru": "https://lenta.ru/rss",
    "РИА Новости": "https://ria.ru/export/rss2/index.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",
    "StopGame": "https://stopgame.ru/rss/rss_news.xml",
    "Kanobu": "https://kanobu.ru/rss/articles/",
    "IXBT Games": "https://www.ixbt.com/export/games.rss",
    "PlayGround": "https://www.playground.ru/rss/news.xml",
    "GameTech": "https://www.gametech.ru/rss/news/"
}

# Глобальные переменные для хранения состояния новостей
news_items = []
current_index = 0

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/news"), KeyboardButton(text="/gaming")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который присылает новости с русских сайтов и новости про игры.\n"
        "Используй команду /news, чтобы получить свежие новости.\n"
        "Используй команду /gaming, чтобы получить новости про игры.",
        reply_markup=keyboard
    )

@dp.message(Command("news"))
async def send_news(message: Message):
    global news_items, current_index
    await message.answer("Собираю новости... Пожалуйста, подождите.", reply_markup=keyboard)

    general_feeds = {k: v for k, v in RSS_FEEDS.items() if k not in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}
    news_items = []

    for source, url in general_feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    news_items.append((source, entry))
            else:
                await message.answer(f"Не удалось получить новости из {source}.", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.", reply_markup=keyboard)

    if news_items:
        current_index = 0
        await show_news(message)

@dp.message(Command("gaming"))
async def send_gaming_news(message: Message):
    global news_items, current_index
    await message.answer("Собираю игровые новости... Пожалуйста, подождите.", reply_markup=keyboard)

    gaming_feeds = {k: v for k, v in RSS_FEEDS.items() if k in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}
    news_items = []

    for source, url in gaming_feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    news_items.append((source, entry))
            else:
                await message.answer(f"Не удалось получить новости из {source}.", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.", reply_markup=keyboard)

    if news_items:
        current_index = 0
        await show_news(message)

async def show_news(message: Message):
    global current_index
    if current_index < len(news_items):
        source, entry = news_items[current_index]
        news_message = (
            f"<b>{source}</b>\n\n"
            f"<b>{entry.title}</b>\n"
            f"{entry.description}\n"
            f"<a href='{entry.link}'>Читать далее</a>"
        )
        # Создаем клавиатуру с кнопками "Предыдущая" и "Следующая"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Предыдущая", callback_data="prev_news"),
                InlineKeyboardButton(text="Следующая ➡️", callback_data="next_news")
            ]
        ])
        await message.answer(news_message, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer("Новости закончились.", reply_markup="keyboard")

@dp.callback_query(lambda c: c.data in ["next_news", "prev_news"])
async def process_callback_navigation(callback_query: CallbackQuery):
    global current_index
    if callback_query.data == "next_news":
        current_index += 1
    elif callback_query.data == "prev_news":
        current_index -= 1

    # Проверяем, чтобы индекс не вышел за пределы списка
    if current_index < 0:
        current_index = 0
    elif current_index >= len(news_items):
        current_index = len(news_items) - 1

    await bot.answer_callback_query(callback_query.id)
    await show_news(callback_query.message)

@dp.message()
async def handle_unknown_command(message: Message):
    await message.answer("Я не понимаю этой команды. Используйте /start для начала.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

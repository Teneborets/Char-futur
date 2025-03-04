import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import feedparser
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

RSS_FEEDS = {
    "Lenta.ru": "https://lenta.ru/rss",
    "РИА Новости": "https://ria.ru/export/rss2/index.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",
    "StopGame": "https://stopgame.ru/rss/news.xml",
    "Kanobu": "https://kanobu.ru/rss/",
    "IXBT Games": "https://www.ixbt.com/export/games.rss",
    "PlayGround": "https://www.playground.ru/rss/news.xml",
    "GameTech": "https://www.gametech.ru/rss/news/"
}

news_items = []
current_index = 0
last_update_time = None
CACHE_DURATION = timedelta(minutes=10)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/news"), KeyboardButton(text="/gaming"), KeyboardButton(text="/update")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который присылает новости с русских сайтов и новости про игры.\n"
        "Используй команду /news, чтобы получить свежие новости.\n"
        "Используй команду /gaming, чтобы получить новости про игры.\n"
        "Используй команду /update, чтобы обновить новости.",
        reply_markup=keyboard
    )

@dp.message(Command("update"))
async def update_news(message: Message):
    global last_update_time
    last_update_time = None
    await fetch_news("news")  # Принудительно обновляем новости
    await message.answer("Новости обновлены.", reply_markup=keyboard)

def ensure_absolute_url(base_url, link):
    if not link:
        return base_url  # Возвращаем базовый URL, если ссылка пуста
    if link.startswith(("http://", "https://")):
        return link
    return urljoin(base_url, link)

async def fetch_news(feed_type):
    global news_items, last_update_time
    if last_update_time and datetime.now() - last_update_time < CACHE_DURATION:
        return

    news_items = []
    feeds = {k: v for k, v in RSS_FEEDS.items() if k not in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]} if feed_type == "news" else \
            {k: v for k, v in RSS_FEEDS.items() if k in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}

    logging.info(f"Используемые RSS-ленты для {feed_type}: {feeds}")  # Логируем используемые ленты

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    entry.link = ensure_absolute_url(url, entry.link)
                    news_items.append((source, entry))
            else:
                logging.warning(f"Не удалось получить новости из {source}.")
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")

    last_update_time = datetime.now()

@dp.message(Command("news"))
async def send_news(message: Message):
    global current_index
    await message.answer("Собираю новости... Пожалуйста, подождите.", reply_markup=keyboard)
    await fetch_news("news")
    if not news_items:
        await message.answer("Новости не найдены. Попробуйте позже.", reply_markup=keyboard)
        return
    current_index = 0
    await show_news(message)

@dp.message(Command("gaming"))
async def send_gaming_news(message: Message):
    global current_index, last_update_time
    last_update_time = None  # Сбрасываем время обновления
    await message.answer("Собираю игровые новости... Пожалуйста, подождите.", reply_markup=keyboard)
    await fetch_news("gaming")
    if not news_items:
        await message.answer("Игровые новости не найдены. Попробуйте позже.", reply_markup=keyboard)
        return
    current_index = 0
    await show_news(message)

async def show_news(message: Message):
    global current_index
    if current_index < len(news_items):
        source, entry = news_items[current_index]
        description = getattr(entry, 'description', '')  # Безопасный доступ к description
        news_message = (
            f"<b>{source}</b>\n\n"
            f"<b>{entry.title}</b>\n"
            f"{description}\n"
            f"<a href='{entry.link}'>Читать далее</a>\n\n"
            f"Новость {current_index + 1} из {len(news_items)}"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Предыдущая", callback_data="prev_news"),
                InlineKeyboardButton(text="В начало", callback_data="start_news"),
                InlineKeyboardButton(text="Следующая ➡️", callback_data="next_news")
            ]
        ])
        await message.answer(news_message, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer("Новости закончились.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data in ["next_news", "prev_news", "start_news"])
async def process_callback_navigation(callback_query: CallbackQuery):
    global current_index
    if callback_query.data == "next_news":
        current_index += 1
    elif callback_query.data == "prev_news":
        current_index -= 1
    elif callback_query.data == "start_news":
        current_index = 0

    if current_index < 0:
        current_index = 0
    elif current_index >= len(news_items):
        current_index = len(news_items) - 1

    await bot.answer_callback_query(callback_query.id)
    await show_news(callback_query.message)

@dp.message()
async def handle_unknown_command(message: Message):
    await message.answer(
        "Неизвестная команда. Используйте /news, /gaming или /update.",
        reply_markup=keyboard
    )

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()  # Закрываем сессию бота

if __name__ == '__main__':
    asyncio.run(main()) 

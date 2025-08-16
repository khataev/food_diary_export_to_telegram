#!/usr/bin/env python3
import sys
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import asyncio
from telegram import Bot, InputMediaPhoto
from telegram.error import RetryAfter

MONTHS_RU = [
    "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
    "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
]

def parse_date_from_filename(filename):
    # Формат имени: YYYY-MM-DDTHH:MM:SS_filename.jpg
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})_.*", filename)
    if not m:
        return None
    year, mon, day, hour, minute, sec = map(int, m.groups())
    return datetime(year, mon, day, hour, minute, sec)

def format_date_for_message(dt):
    return f"{dt.day} {MONTHS_RU[dt.month-1]}"

async def send_media_group_with_retry(bot, chat_id, media_group, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            await bot.send_media_group(chat_id=chat_id, media=media_group)
            return
        except RetryAfter as e:
            wait_time = e.retry_after
            print(f"Flood control: ждем {wait_time} секунд...")
            await asyncio.sleep(wait_time)
            retries += 1
        except TimedOut:
            retres = max_retries
            print(f"Ошибка TimedOut")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
    print("Превышено максимальное число попыток отправки.")

async def main():
    if len(sys.argv) != 4:
        print("Usage: send_photos.py <path_to_photos> <bot_token> <chat_id>")
        sys.exit(1)

    photos_dir = sys.argv[1]
    bot_token = sys.argv[2]
    chat_id = sys.argv[3]

    p = Path(photos_dir)
    if not p.is_dir():
        print(f"Directory not found: {photos_dir}")
        sys.exit(2)

    files = [f.name for f in p.glob('*.jpg')]
    if not files:
        print("No .jpg files found in the directory.")
        sys.exit(0)

    groups = defaultdict(list)
    for f in files:
        dt = parse_date_from_filename(f)
        if dt is None:
            print(f"Warning: filename doesn't match expected pattern: {f}")
            continue
        date_key = dt.date()
        groups[date_key].append((dt, f))

    bot = Bot(token=bot_token)

    for date_key in sorted(groups.keys()):
        groups[date_key].sort(key=lambda x: x[0])
        message_text = format_date_for_message(datetime(date_key.year, date_key.month, date_key.day))

        print(f"\nОтправка сообщения за {message_text}")
        answer = input("Отправить? (Y/n): ").strip().lower()
        if answer == 'n':
            print("Пропускаем.")
            continue
        # Если answer == '' или любой другой символ — отправляем

        media_group = []
        for i, (_, filename) in enumerate(groups[date_key]):
            path = p / filename
            if i == 0:
                media_group.append(InputMediaPhoto(open(path, "rb"), caption=message_text))
            else:
                media_group.append(InputMediaPhoto(open(path, "rb")))

        await send_media_group_with_retry(bot, chat_id, media_group)

        print("Сообщение отправлено.")

if __name__ == "__main__":
    asyncio.run(main())

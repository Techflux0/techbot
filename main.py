# start here
import os
import asyncio
import aiohttp
import ssl
import certifi
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from storage.database import init_db, add_user, add_bad_word, remove_bad_word, get_bad_words, get_users, is_bad_word_in_message, warn_user, get_user_warns, get_group_config, update_group_config, add_authorized_user, remove_authorized_user, is_authorized_user
from poison.gemini import is_offensive_with_gemini
from storage.database import add_quote, get_quote, enable_quotes, disable_quotes, get_all_enabled_groups, get_all_quotes
from datetime import datetime
from poison.checks import check_dependencies
from poison.quotes import fetch_quote

from poison.checks import check_dependencies
check_dependencies()


load_dotenv()
AUTHORIZED_USER_ID = int(os.getenv("USER_ID", 0))
TOKEN = os.getenv("BOT_TOKEN")
def is_authorized(message: Message):
    return message.from_user.id == AUTHORIZED_USER_ID

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Starting bot...")

logger.info("Bot started.")
logger.info("Bot is running...")
logger.info("Bot is ready.")
logger.info("Bot is online.")
logger.info("Bot is operational.")
logger.info("Bot is active.")

#log errors into a file
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)
logger.error("Error occurred: %s", "Error message here")
logger.info("Error logging initialized.")
logger.info("Bot is ready to receive commands.")
logger.info("Bot is ready to process messages.")
logger.info("Bot is ready to handle commands.")
# get enabled groups
@dp.message(Command("id"))
async def test_is_command(message: Message):
    id = message.from_user.id
    await message.answer(F"Your id: <code>{id}</code>")

# get_all_quotes
@dp.message(Command("quotes"))
async def get_all_quotes_handler(message: Message):
    quotes = get_all_quotes()
    if not quotes:
        await message.answer("No quotes found.")
    else:
        response = "Quotes:\n"
        for quote, author in quotes:
            response += f"<b>{quote}</b> — <i>{author}</i>\n"
        await message.answer(response)

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    add_user(user_id, full_name)
    await message.answer(f"Hello <b>{full_name}</b>! You've been saved to the DB.")


@dp.message(Command("kick"))
async def kick_command(message: types.Message):
    if not is_authorized(message):
        await message.answer("You are not authorized to use this command.")
        return

    if message.chat.type not in ("group", "supergroup"):
        await message.answer("This command can only be used in groups.")
        return

    args = message.text.split(' ')[1].strip().lower()
    if args not in ['on', 'off']:
        await message.answer("Usage: /kick <on/off>")
        return

    kick_enabled = True if args == 'on' else False
    group_id = message.chat.id
    update_group_config(group_id, kick_enabled, None) 
    await message.answer(f"Kick setting updated to {args.upper()} for this group.")

@dp.message(Command("ban"))
async def ban_command(message: types.Message):
    if not is_authorized(message):
        await message.answer("You are not authorized to use this command.")
        return

    if message.chat.type not in ("group", "supergroup"):
        await message.answer("This command can only be used in groups.")
        return

    args = message.text.split(' ')[1].strip().lower()
    if args not in ['on', 'off']:
        await message.answer("Usage: /ban <on/off>")
        return

    ban_enabled = True if args == 'on' else False
    group_id = message.chat.id
    _, kick_enabled = get_group_config(group_id) 
    update_group_config(group_id, kick_enabled, ban_enabled)
    await message.answer(f"Ban setting updated to {args.upper()} for this group.")

@dp.message(Command("bad"))
async def add_bad_words_handler(message: Message):
    args = message.text.replace('/bad', '').strip()
    if not args:
        await message.answer("Usage: <code>/bad word1, word2, word3</code>")
        return

    words = [word.strip().lower() for word in args.split(',') if word.strip()]
    added = []
    skipped = []

    for word in words:
        if add_bad_word(word):
            added.append(word)
        else:
            skipped.append(word)

    response = ""
    if added:
        response += f"✅ Added: <b>{', '.join(added)}</b>\n"
    if skipped:
        response += f"⚠️ Already exists: <b>{', '.join(skipped)}</b>"

    await message.answer(response or "Nothing happened.")

@dp.message(Command("removebad"))
async def remove_bad_words_handler(message: Message):
    args = message.text.replace('/removebad', '').strip()
    if not args:
        await message.answer("Usage: <code>/removebad word1, word2, word3</code>")
        return

    words = [word.strip().lower() for word in args.split(',') if word.strip()]
    removed = []
    not_found = []

    for word in words:
        if remove_bad_word(word):
            removed.append(word)
        else:
            not_found.append(word)

    response = ""
    if removed:
        response += f"✅ Removed: <b>{', '.join(removed)}</b>\n"
    if not_found:
        response += f"⚠️ Not found: <b>{', '.join(not_found)}</b>"

    await message.answer(response or "Nothing happened.")


def is_authorized(user_id):
    return user_id == AUTHORIZED_USER_ID

@dp.message(Command("add"))
async def add_authorized_user_handler(message: Message):
    if not is_authorized(message.from_user.id):
        await message.answer("<code>You are not authorized to use this command.</code>")
        return

    args = message.text.split(' ')[1:]
    if len(args) != 1:
       # await message.answer("Usage: /add <user_id>")
        return
    user_id = int(args[0])
    if add_authorized_user(user_id):
        await message.answer(f"User added to the authorized users list.")
    else:
        await message.answer(f"User is already in the authorized users list.")

# # /remove <user_id> command to remove a user from the authorized users list
@dp.message(Command("remove"))
async def remove_authorized_user_handler(message: Message):
    if not is_authorized(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return

    args = message.text.split(' ')[1:]
    if len(args) != 1:
        await message.answer("Usage: /remove <user_id>")
        return

    user_id = int(args[0])

    if remove_authorized_user(user_id):
        # Send a plain message without any formatting
        await message.answer(f"User with ID {user_id} has been removed from the authorized users list.")
    else:
        # Ensure this message also does not contain any formatting issues
        await message.answer(f"User with ID {user_id} is not in the authorized users list.")


#@dp.message(Command("badwords"))
@dp.message(Command("badwords"))
async def get_bad_words_handler(message: Message):
    words = get_bad_words()
    if not words:
        await message.answer("No bad words found.")
    else:
        await message.answer(f"Bad words: <code>{', '.join(words)}</code>")

@dp.message(Command("users"))
async def get_users_handler(message: Message):
    users = get_users()
    if not users:
        await message.answer("No users found.")
    else:
        response = "Users:\n"
        for user_id, name, warns in users:
            response += f"<b>{name}</b> (<code>{user_id}</code>) - Warns: <b>{warns}</b>\n"
        await message.answer(response)

@dp.message()
async def monitor_bad_words(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    if not message.text:
        return

    if message.chat.type == 'supergroup' or message.chat.type == 'group':
        admins = await message.chat.get_administrators()
        admin_user_ids = [admin.user.id for admin in admins]

        if message.from_user.id in admin_user_ids:
            return 

    if is_bad_word_in_message(message.text):# or is_offensive_with_gemini(message.text):
        try:
            await message.delete()

            group_id = message.chat.id
            kick_enabled, ban_enabled = get_group_config(group_id)

            if kick_enabled:
                await message.chat.kick(message.from_user.id)
                await message.answer(f"🚫 {message.from_user.first_name} has been kicked for using inappropriate language.")

            if ban_enabled:
                await message.chat.ban(message.from_user.id)
                await message.answer(f"🚫 {message.from_user.first_name} has been banned for using inappropriate language.")
            
        except Exception as e:
            print(f"Error: {e}")

quote = os.getenv("QUOTES")
def get_time_slot():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

async def fetch_quote():
    url = "https://api.api-ninjas.com/v1/quotes"
    headers = {"X-Api-Key": quote}
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            if data:
                return data[0]["quote"], data[0]["author"]
    return None, None

@dp.message(Command("getquote"))
async def getquote(message: Message):
    quote, author = await fetch_quote()
    if quote and author:
        await message.reply(f"🧠 <b>{quote}</b>\n— <i>{author}</i>")
    else:
        await message.reply("❌ Failed to fetch quote.")

@dp.message(Command("quote"))
async def quote_toggle(message: Message):
    cmd = message.text.split()
    if len(cmd) < 2 or cmd[1] not in ("on", "off"):
        await message.reply("Usage: /quote on | /quote off")
        return

    group_id = message.chat.id
    if cmd[1] == "on":
        enable_quotes(group_id)
        await message.reply("✅ Quotes enabled for this group.")
    else:
        disable_quotes(group_id)
        await message.reply("❌ Quotes disabled for this group.")

# Keeps fetching and storing quotes every minute
async def quote_fetcher_loop():
    while True:
        time_slot = get_time_slot()
        quote, author = await fetch_quote()
        if quote and author:
            add_quote(quote, author, time_slot)
        await asyncio.sleep(60)  # Every 60 seconds

# Sends the correct time slot quote to all groups
async def quote_sender_loop():
    last_sent_slot = None
    while True:
        current_slot = get_time_slot()
        if current_slot != last_sent_slot:
            quote_data = get_quote(current_slot)
            if quote_data:
                quote, author = quote_data
                text = f"<b>{current_slot.title()} Quote:</b>\n🧠 {quote} — <i>{author}</i>"
                for group_id in get_all_enabled_groups():
                    await bot.send_message(group_id, text)
            last_sent_slot = current_slot
        await asyncio.sleep(60)  # Every 60 seconds

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

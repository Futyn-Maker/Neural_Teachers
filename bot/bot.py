import asyncio
from datetime import time

from scheduler.asyncio import Scheduler

from loguru import logger

from vkbottle import API
from vkbottle import Keyboard, KeyboardButtonColor, Callback, GroupEventType
from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Bot, BotLabeler, Message, MessageEvent, rules

from generator import Generator
from db import Db

from config import VK_TOKEN, VK_SERVICE_TOKEN, GROUP_ID


logger.add("bot.log")  # set the log entry to file

bot = Bot(VK_TOKEN)
bot.labeler.vbml_ignore_case = True  # make message handlers case-insensitive
bot.labeler.load(BotLabeler())

service_api = API(VK_SERVICE_TOKEN)  # to post on the wall

generator = Generator()
db = Db()

# Set a keyboard for messages with quotes
keyboard = Keyboard(inline=True)
keyboard.add(Callback("😁 Круто!", {"cmd": "like"}),
             KeyboardButtonColor.POSITIVE)
keyboard.add(Callback("🙍 Что-то не то...", {"cmd": "dislike"}),
             KeyboardButtonColor.NEGATIVE)
keyboard = keyboard.get_json()


async def main():
    """The main function in which we configure and run the bot, as well as
    run the scheduler"""
    await generator.init_generator()
    await db.init_db()

    @bot.on.message()
    async def send_quote(message: Message):
        if message.text.lower() == "/рандом":
            prompt = ""
        else:
            prompt = message.text
        # Emulate text typing
        await bot.api.messages.set_activity(
            peer_id=message.peer_id,
            type="typing"
        )

        quotes = await generator.generate(prompt)
        if prompt:
            quote = quotes[0].strip()  # only the first sample is appropriate
            await message.answer(quote, keyboard=keyboard)
        else:
            # We can send several generated quotes
            for quote in quotes:
                await message.answer(quote.strip(), keyboard=keyboard)

    # Handle button clicks
    @bot.on.raw_event(
        GroupEventType.MESSAGE_EVENT,
        MessageEvent,
        rules.PayloadRule({"cmd": "like"}),
    )
    async def handle_liked_quote(event: MessageEvent):
        # Get the text of the message to add to the database
        message = await bot.api.messages.get_by_conversation_message_id(
            peer_id=event.peer_id,
            conversation_message_ids=[event.conversation_message_id]
        )
        text = message.items[0].text
        await event.edit_message(f"✅ {text}", keyboard=EMPTY_KEYBOARD)
        await db.add_quote(text, "liked")
        await event.show_snackbar(
            "🎉 Отлично! Эта цитата добавлена в очередь на публикацию на стене!"
        )

    @bot.on.raw_event(
        GroupEventType.MESSAGE_EVENT,
        MessageEvent,
        rules.PayloadRule({"cmd": "dislike"}),
    )
    async def handle_disliked_quote(event: MessageEvent):
        message = await bot.api.messages.get_by_conversation_message_id(
            peer_id=event.peer_id,
            conversation_message_ids=[event.conversation_message_id]
        )
        text = message.items[0].text
        await event.edit_message(f"❌ {text}", keyboard=EMPTY_KEYBOARD)
        await db.add_quote(text, "disliked")
        await event.show_snackbar(
            "🤔 Что ж, бывает. Спрячем эту неудачную цитату подальше."
        )

    await asyncio.gather(bot.run_polling(), set_scheduler(post_quote))


async def post_quote():
    """Posts quotes liked by users on the group's wall"""
    posted_quote = await db.get_random_quote()
    if not posted_quote:
        posted_quote = await generator.generate()
        quote = posted_quote[0].strip()
    else:
        quote = posted_quote["quote"]

    await service_api.wall.post(owner_id=GROUP_ID, from_group=True,
                                message=quote)

    await db.del_quote(posted_quote["id"])
    await db.add_quote(quote, "posted")


async def set_scheduler(func):
    """Forces the specified function to be executed every half hour, exactly at 00 and 30 minutes"""
    schedule = Scheduler()
    schedule.hourly(time(minute=30), func)
    schedule.hourly(time(), func)
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

import logging
from aiogram import types

logger = logging.getLogger("zoo_bot.sharing")


async def share_result(message: types.Message, totem_key: str, user_name: str):
    bot_username = None
    if hasattr(message, "bot") and message.bot:
        try:
            bot_info = await message.bot.get_me()
            bot_username = bot_info.username
        except Exception:
            logger.exception("Не удалось получить username бота")
    if not bot_username:
        bot_username = "SFTGZooBot"
    bot_mention = f"@{bot_username.lstrip('@')}"

    text = (
        f"Я прошёл викторину от Московского зоопарка "
        f"и узнал, что моё тотемное животное — *{totem_key}*!\n\n"
        f"Хочешь узнать, кто ты? → {bot_mention}\n\n"
        f"Пройди и ты 👉 {bot_mention}"
    )

    logger.info(f"share_result: user_id={message.from_user.id}, totem={totem_key}")
    await message.answer(text, parse_mode="Markdown")

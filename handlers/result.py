import os
import json
import logging
from typing import Optional

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.media import generate_image
from services.media import compress_image_if_needed
from services.scoring import calculate_scores, get_top_animal

router = Router()
logger = logging.getLogger("zoo_bot.result")

ANIMALS_PATH = os.path.join("data", "results.json")
with open(ANIMALS_PATH, encoding="utf-8") as f:
    ANIMALS = json.load(f)


async def show_result(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", [])

    scores = calculate_scores(answers)
    top = get_top_animal(scores)
    if top is None:
        await message.answer("⚠️ Не удалось определить ваш тотем. Попробуйте ещё раз.")
        await state.clear()
        return

    totem_key, totem_score = top
    animal = ANIMALS.get(totem_key)
    if not animal:
        logger.error(f"Totem key '{totem_key}' отсутствует в animals.json")
        await message.answer("⚠️ Произошла ошибка при определении тотема.")
        await state.clear()
        return

    logger.info(f"Пользователь {message.from_user.id} — тотем: {animal['name']} ({totem_score} очков)")

    image_path: Optional[str]
    try:
        image_path = await generate_image(
            image_path=animal["image"],
            animal_name=animal["name"],
            user_name=message.from_user.first_name
        )
    except Exception:
        logger.exception("Ошибка при генерации итоговой картинки")
        image_path = None

    caption = (
        f"🎉 *Твоё тотемное животное — {animal['name']}!*\n\n"
        f"_{animal['description']}_\n\n"
        f"[Узнать об опеке]({animal['guardian_link']})"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Ещё раз", callback_data="start_quiz")],
        [InlineKeyboardButton(text="📢 Поделиться", callback_data=f"share_{totem_key}")],
        [InlineKeyboardButton(text="💬 Отзыв", callback_data="feedback")],
        [InlineKeyboardButton(text="📞 Связаться", callback_data=f"contact_{totem_key}")]
    ])
    if image_path:
        image_path = await compress_image_if_needed(image_path)

    if image_path:
        await message.answer_photo(
            photo=types.FSInputFile(image_path),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=kb
        )
    else:
        await message.answer(caption, parse_mode="Markdown", reply_markup=kb)

    await state.clear()

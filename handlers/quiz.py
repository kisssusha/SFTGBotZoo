import json
import os
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger("zoo_bot.quiz")

class Quiz(StatesGroup):
    question = State()

QUIZ_PATH = os.path.join("data", "questions.json")
with open(QUIZ_PATH, encoding="utf-8") as f:
    QUESTIONS = json.load(f)
TOTAL_QUESTIONS = len(QUESTIONS)
logger.info(f"Загружено {TOTAL_QUESTIONS} вопросов для викторины")

@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(current=0, answers=[])
    logger.info(f"Пользователь {callback.from_user.id} начинает викторину")
    await send_question(callback.message, 0, state)
    await callback.answer()

async def send_question(message: Message, index: int, state: FSMContext):
    if index >= TOTAL_QUESTIONS:
        logger.info(f"Пользователь {message.from_user.id} ответил на все вопросы")
        await message.answer("🧠 Обработка результатов…")
        await state.set_state(None)
        from handlers.result import show_result
        await show_result(message, state)
        return

    q = QUESTIONS[index]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ans["text"],
                    callback_data=f"quiz_{index}_{i}"
                )
            ]
            for i, ans in enumerate(q["answers"])
        ]
    )
    await message.answer(
        f"❓ Вопрос {index+1}/{TOTAL_QUESTIONS}:\n{q['question']}",
        reply_markup=keyboard
    )
    await state.set_state(Quiz.question)

@router.callback_query(F.data.startswith("quiz_"))
async def answer_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data.get("current", 0)
    answers = data.get("answers", [])

    _, q_idx_str, a_idx_str = callback.data.split("_")
    q_idx, a_idx = int(q_idx_str), int(a_idx_str)

    selected_weights = QUESTIONS[q_idx]["answers"][a_idx]["weights"]
    answers.append(selected_weights)
    await state.update_data(current=current + 1, answers=answers)

    await callback.message.edit_reply_markup(None)

    logger.debug(
        f"Пользователь {callback.from_user.id} выбрал ответ {a_idx} для вопроса {q_idx}"
    )

    await send_question(callback.message, current + 1, state)
    await callback.answer()

import os
import logging

from aiogram import Router, types, F

router = Router()
logger = logging.getLogger("zoo_bot.contact")

@router.callback_query(F.data.startswith("contact_"))
async def contact_user(callback: types.CallbackQuery):
    totem_key = callback.data.replace("contact_", "")
    user = callback.from_user

    staff_info = (
        "📩 Новый контактный запрос:\n"
        f"👤 Пользователь: @{user.username or user.full_name} (ID: {user.id})\n"
        f"🐾 Тотем: {totem_key}\n"
    )

    try:
        os.makedirs("data", exist_ok=True)
        contact_path = os.path.join("data", "contact_requests.txt")
        with open(contact_path, "a", encoding="utf-8") as f:
            f.write(staff_info + "\n")
        logger.info(f"Contact request saved: user_id={user.id}, totem={totem_key}")
    except Exception:
        logger.exception("Ошибка при сохранении контактного запроса")

    await callback.message.answer(
        "📧 Ваш запрос отправлен сотруднику зоопарка! Мы свяжемся с вами в ближайшее время."
    )
    await callback.answer()

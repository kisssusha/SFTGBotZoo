from aiogram import Router
from handlers import start, quiz, result, feedback, contact, sharing

router = Router()

router.include_router(start.router)
router.include_router(quiz.router)
router.include_router(result.router)
router.include_router(feedback.router)
router.include_router(contact.router)
router.include_router(sharing.router)

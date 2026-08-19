from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka, inject
from src.repositories.service_password import ServicePasswordRepository
from src.bot.state import AccessState
from src.models.postgres import User
from src.repositories.users import UserRepository
from src.bot.keyboards import main_menu_keyboard
from src.core.config import settings 

router = Router()


@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
    user_repo: FromDishka[UserRepository]
):
    telegram_id=message.from_user.id
    user = await user_repo.get_by_tg_id(telegram_id)
    if not user:
        user = await user_repo.create(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

    if not user.has_passed:
        await state.set_state(AccessState.waiting_for_password)
        await message.answer(
            "🔐 Введите пароль доступа:"
        )
        return
    
    await message.answer(
        "С возвращением!",
        reply_markup=main_menu_keyboard,
    )



@router.message(AccessState.waiting_for_password)
@inject
async def check_service_password(
    message: Message,
    state: FSMContext,
    user_repo: FromDishka[UserRepository],
    service_password_repo: FromDishka[ServicePasswordRepository]
):
    password = await service_password_repo.get()
    if message.text != password:
        await message.answer(
            "❌ Неверный пароль.\n"
            "Попробуйте ещё раз:"
        )
        return
    user = await user_repo.get_by_tg_id(telegram_id=message.from_user.id)
    if not user:
        return 
    
    user.has_passed = True
    await service_password_repo.refresh()
    await state.clear()
    await message.answer(
        "✅ Доступ разрешён!",
        reply_markup=main_menu_keyboard,
    )
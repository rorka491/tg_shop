from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from src.bot.keyboards import cart_keyboard
from src.models.postgres import User
from src.repositories.order import OrderRepository
from src.enums import MainMenu
from src.bot.commands import AddToOrderCommand, RemoveFromOrderCommand, ClearCartCommand
from src.bot.callback_data import CartCallback
from src.bot.formaters import order_formatter

router = Router()


@router.message(F.text == MainMenu.CART)
@inject
async def cart(
    message: Message,
    user: FromDishka[User], 
    order_repo: FromDishka[OrderRepository],
):
    await message.delete()
    order = await order_repo.get_pending_by_user_id(user.id)
    if not order or not order.products:
        await message.answer("🛒 Корзина пуста")
        return
    
    await message.answer(**order_formatter(order).as_kwargs(), reply_markup=cart_keyboard())


    
@router.callback_query(
    CartCallback.filter(F.action == "add")
)
@inject
async def add_to_cart(
    callback: CallbackQuery,
    callback_data: CartCallback,
    command: FromDishka[AddToOrderCommand]
):
    return await command.execute(
        product_id=callback_data.product_id,
        callback=callback,
    )

@router.callback_query(
    CartCallback.filter(F.action == "remove")
)
@inject
async def remove_from_cart(
    callback: CallbackQuery,
    callback_data: CartCallback,
    command: FromDishka[RemoveFromOrderCommand]
):
    return await command.execute(
        product_id=callback_data.product_id,
        callback=callback,
    )


@router.callback_query(
    CartCallback.filter(F.action == "clear")
)
@inject
async def clear_cart(
    callback: CallbackQuery,
    command: FromDishka[ClearCartCommand]
):
    return await command.execute(callback)

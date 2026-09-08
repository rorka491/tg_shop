from datetime import datetime

from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.repositories.users import UserRepository
from src.bot.state import DeliveryState, SelfPickUpState
from src.enums import CallbackAction, MainMenu, OrderStatus
from src.bot.keyboards import order_type_keyboard, pickup_confirmation_keyboard
from src.models.postgres import User
from src.repositories.order import OrderRepository
from src.bot.callback_data import CartCallback, OrderCallback
from dishka.integrations.aiogram import FromDishka, inject
from src.bot.keyboards import location_keyboard
from src.bot.formaters import admin_order_formatter, list_order_formatter

router = Router()

@router.callback_query(
    CartCallback.filter(F.action == CallbackAction.ORDER)
)
@inject
async def order_option(
    callback: CallbackQuery,
    user: FromDishka[User],
    state: FSMContext,
    order_repo: FromDishka[OrderRepository]
):
    order = await order_repo.get_pending_by_user_id(user.id)
    if not order:
        return
    
    await callback.message.delete()
    await callback.message.answer(
        "Выберите тип заказа",
        reply_markup=order_type_keyboard(order)
    )
    await callback.answer()


@router.callback_query(
    OrderCallback.filter(F.action == CallbackAction.SELF_PICKUP)
)
async def self_pickup_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(
        SelfPickUpState.waiting_for_date_time
    )
    await callback.message.edit_text(
        "📅 Укажите дату и время самовывоза.\n\n"
        "Например: 20.08.2026 18:30"
    )

    await callback.answer()


@router.message(SelfPickUpState.waiting_for_date_time)
async def pickup_date_time(
    message: Message,
    state: FSMContext,
):
    try:
        pickup_at = datetime.strptime(
            message.text,
            "%d.%m.%Y %H:%M",
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Введите дату и время так:\n"
            "20.08.2026 18:30"
        )
        return

    await state.update_data(
        pickup_at=pickup_at.isoformat(),
    )
    

    await state.set_state(
        SelfPickUpState.waiting_for_confirmation
    )

    await message.answer(
        f"📅 Самовывоз:\n"
        f"{pickup_at:%d.%m.%Y %H:%M}\n\n"
        "Всё верно?",
        reply_markup=pickup_confirmation_keyboard(),
    )

@router.callback_query(
    SelfPickUpState.waiting_for_confirmation,
    OrderCallback.filter(F.action == CallbackAction.CONFIRM_ORDER),
)
@inject
async def confirm_pickup(
    callback: CallbackQuery,
    state: FSMContext,
    user: FromDishka[User],
    order_repo: FromDishka[OrderRepository],
    user_repo: FromDishka[UserRepository],
    bot: FromDishka[Bot],
):
    data = await state.get_data()
    pickup_at = datetime.fromisoformat(data["pickup_at"])

    await state.clear()
    order = await order_repo.get_pending_by_user_id(user.id)
    if not order: 
        return
    order.status = OrderStatus.paid
    order.pickup_at = pickup_at
    order = await order_repo.save(order)
    admins = await user_repo.get_all_admins()
    for admin in admins:
        await bot.send_message(
            text=admin_order_formatter(order),
            chat_id=admin.telegram_id,
        )

    await callback.message.edit_text(
        "✅ Заказ оформлен!\n\n"
        f"📅 Самовывоз: {pickup_at:%d.%m.%Y %H:%M}"
    )

    await callback.answer()


@router.callback_query(
    OrderCallback.filter(F.action == CallbackAction.DELIVERY)
)
async def delivery_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(
        DeliveryState.waiting_for_address
    )

    await callback.message.delete()

    await callback.message.answer(
        "📍 Укажите адрес доставки текстом "
        "или отправьте геопозицию:",
        reply_markup=location_keyboard,
    )

    await callback.answer()


@router.message(DeliveryState.waiting_for_address)
async def delivery_address(
    message: Message,
    state: FSMContext,
):
    if message.location:
        await state.update_data(
            latitude=message.location.latitude,
            longitude=message.location.longitude,
        )

    elif message.text:
        await state.update_data(
            delivery_address=message.text,
        )

    else:
        await message.answer(
            "❌ Отправьте адрес текстом или геопозицию."
        )
        return

    await state.set_state(
        DeliveryState.waiting_for_date_time
    )

    await message.answer(
        "📅 Укажите дату и время доставки.\n\n"
        "Например: 20.08.2026 18:30",
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message(DeliveryState.waiting_for_date_time)
async def delivery_date_time(
    message: Message,
    state: FSMContext,
):
    try:
        delivery_at = datetime.strptime(
            message.text,
            "%d.%m.%Y %H:%M",
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Введите дату и время так:\n"
            "20.08.2026 18:30"
        )
        return

    await state.update_data(
        delivery_at=delivery_at.isoformat(),
    )

    data = await state.get_data()

    await state.set_state(
        DeliveryState.waiting_for_confirmation
    )

    await message.answer(
        "🚚 Подтвердите заказ\n\n"
        f"📍 Адрес: {data['delivery_address']}\n"
        f"📅 Доставка: {delivery_at:%d.%m.%Y %H:%M}",
        reply_markup=pickup_confirmation_keyboard(),
    )

@router.callback_query(
    DeliveryState.waiting_for_confirmation,
    OrderCallback.filter(F.action == CallbackAction.CONFIRM_ORDER),
)
@inject
async def confirm_delivery(
    callback: CallbackQuery,
    state: FSMContext,
    user: FromDishka[User],
    order_repo: FromDishka[OrderRepository],
    user_repo: FromDishka[UserRepository],
    bot: FromDishka[Bot],
):
    data = await state.get_data()

    delivery_at = datetime.fromisoformat(
        data["delivery_at"]
    )

    delivery_address = data["delivery_address"]

    await state.clear()

    order = await order_repo.get_pending_by_user_id(
        user.id
    )

    if not order:
        return

    order.status = OrderStatus.paid
    order.delivery_address = delivery_address
    order.delivery_at = delivery_at

    order = await order_repo.save(order)

    admins = await user_repo.get_all_admins()

    for admin in admins:
        await bot.send_message(
            chat_id=admin.telegram_id,
            text=admin_order_formatter(order),
        )

    await callback.message.edit_text(
        "✅ Заказ оформлен!\n\n"
        f"📍 Адрес: {delivery_address}\n"
        f"📅 Доставка: {delivery_at:%d.%m.%Y %H:%M}"
    )

    await callback.answer()



@router.message(F.text == MainMenu.ORDERS)
async def get_my_orders(
    message: Message,
    user: FromDishka[User],
    order_repo: FromDishka[OrderRepository]    
):
    await message.delete()
    orders = await order_repo.all_user_orders(user.id)
    await message.answer(list_order_formatter(orders))

    
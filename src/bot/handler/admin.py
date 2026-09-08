from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from src.repositories.order import OrderRepository
from src.enums import CallbackAction, OrderStatus
from src.bot.formaters import admin_formatter, admin_order_formatter, order_formatter, product_formatter
from src.repositories import ProductRepository, ServicePasswordRepository
from src.bot.callback_data import AdminCallback, AdminOrderCallback
from src.models.postgres.user import User
from src.bot.keyboards import admin_keyboard, admin_order_keyboard, admin_product_keyboard
from src.bot.state import AddProductState, ChangePrice, UpdateProductState
from src.core.config import settings 
from pathlib import Path
from uuid import UUID, uuid4


router = Router()


@router.message(Command("admin"))
@inject
async def admin(
    message: Message,
    user: FromDishka[User],
    service_password_repo: FromDishka[ServicePasswordRepository]
):
    await message.delete()
    if not user.is_admin:
        await message.answer("⛔️ Доступ запрещён.")
        return

    password = await service_password_repo.get()
    if not password:
        password = await service_password_repo.refresh()

    await message.answer(
        **admin_formatter(password).as_kwargs(),
        reply_markup=admin_keyboard(),
    )

@router.callback_query(
    AdminCallback.filter(F.action == "add")
)
@inject
async def create_product_start(
    callback: CallbackQuery,
    user: FromDishka[User],
    state: FSMContext,
):
    if not user.is_admin:
        await callback.answer(
            "⛔️ Доступ запрещён",
            show_alert=True,
        )
        return

    await state.set_state(AddProductState.name)

    await callback.message.answer(
        "Введите название товара:"
    )

    await callback.answer()


@router.message(AddProductState.name)
async def product_name(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer("Введите название текстом.")
        return

    await state.update_data(name=message.text)
    await state.set_state(AddProductState.description)

    await message.answer(
        "Введите описание товара:"
    )

@router.message(AddProductState.description)
async def product_description(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer("Введите описание текстом.")
        return

    await state.update_data(description=message.text)
    await state.set_state(AddProductState.unit)

    await message.answer(
        "Введите единицу измерения товара:"
    )


@router.message(AddProductState.unit)
async def product_unit(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer("Введите описание текстом.")
        return
    
    await state.update_data(unit=message.text)
    await state.set_state(AddProductState.price)

    await message.answer(
        "Введите цену товара:"
    )

@router.message(AddProductState.price)
async def product_price(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer("Введите цену целым числом.")
        return

    try:
        price = int(message.text)
    except ValueError:
        await message.answer(
            "Некорректная цена. Например: 500"
        )
        return

    if price <= 0:
        await message.answer(
            "Цена должна быть больше 0"
        )
        return

    await state.update_data(price=price)
    await state.set_state(AddProductState.stock)

    await message.answer(
        "Введите количество товара на складе:"
    )

@router.message(AddProductState.stock)
async def product_stock(
    message: Message,
    state: FSMContext,
):
    if not message.text or not message.text.isdigit():
        await message.answer("Введите целое число.")
        return

    stock = int(message.text)

    await state.update_data(stock=stock)
    await state.set_state(AddProductState.preview)

    await message.answer(
        "Отправьте фотографию товара:"
    )



@router.message(AddProductState.preview, F.photo)
async def product_preview(
    message: Message,
    state: FSMContext,
    product_repo: FromDishka[ProductRepository],
    bot: FromDishka[Bot],
):
    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)

    filename = f"{uuid4()}.jpg"
    path = settings.upload_dir / filename

    settings.upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    await bot.download_file(
        file.file_path,
        destination=path,
    )

    data = await state.get_data()

    product = await product_repo.create(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        stock=data["stock"],
        preview=str(path),
        is_active=True,
    )

    await state.clear()

    await message.answer(
        f"✅ <b>Товар создан</b>\n\n"
        f"📦 {product.name}\n"
        f"💰 {product.price} ₽\n"
        f"📊 Остаток: {product.stock} {product.unit}."
    )


@router.callback_query(
    AdminCallback.filter(F.action == "nomenclature")
)
@inject
async def nomenclature(
    callback: CallbackQuery,
    product_repo: FromDishka[ProductRepository]
): 
    products = await product_repo.get_all()
    for product in products:
        await callback.message.answer(
            product_formatter(product),
            reply_markup=admin_product_keyboard(product)
        )
    await callback.answer()

@router.callback_query(
    AdminCallback.filter(F.action == CallbackAction.PRICE)
)
async def change_price_callback(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    state: FSMContext,
    product_repo: FromDishka[ProductRepository],
):
    product = await product_repo.get_by_id(callback_data.product_id)

    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    await state.set_state(ChangePrice.waiting_for_price)
    await state.update_data(product_id=str(product.id))

    await callback.message.answer(
        f"💰 Текущая цена: <b>{product.price} ₽</b>\n\n"
        "Введите новую цену:"
    )

    await callback.answer()


@router.message(ChangePrice.waiting_for_price)
async def change_price(
    message: Message,
    state: FSMContext,
    product_repo: FromDishka[ProductRepository],
    order_repo: FromDishka[OrderRepository],
):
    try:
        price = int(message.text)
    except (TypeError, ValueError):
        await message.answer("❌ Введите цену числом.")
        return

    if price <= 0:
        await message.answer("❌ Цена должна быть больше 0.")
        return

    data = await state.get_data()
    product_id = data["product_id"]

    product = await product_repo.get_by_id(product_id)

    if not product:
        await message.answer("❌ Товар не найден.")
        await state.clear()
        return

    product.price = price
    await order_repo.recalculate_pending_product_price(product.id, product.price)

    await state.clear()

    await message.answer(
        f"✅ Цена товара <b>{product.name}</b> изменена.\n"
        f"Новая цена: <b>{price} ₽</b>"
    )

@router.callback_query(
    AdminCallback.filter(F.action == "stock")
)
@inject
async def update_stock_start(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    user: FromDishka[User],
    state: FSMContext,
):
    if not user.is_admin:
        await callback.answer(
            "⛔️ Доступ запрещён",
            show_alert=True,
        )
        return

    await state.update_data(
        product_id=str(callback_data.product_id),
    )

    await state.set_state(UpdateProductState.stock)

    await callback.message.answer(
        "📦 Введите новый остаток:"
    )

    await callback.answer()


@router.message(UpdateProductState.stock)
@inject
async def update_stock(
    message: Message,
    state: FSMContext,
    product_repo: FromDishka[ProductRepository],
):
    if not message.text or not message.text.isdigit():
        await message.answer(
            "Введите целое число."
        )
        return

    stock = int(message.text)

    data = await state.get_data()
    product_id = UUID(data["product_id"])

    product = await product_repo.get_by_id(product_id)

    if product is None:
        await state.clear()
        await message.answer("❌ Товар не найден.")
        return

    product.stock = stock

    await product_repo.save(product)

    await state.clear()

    await message.answer(
        f"✅ Остаток изменён\n\n"
        f"📦 {product.name}\n"
        f"Остаток: {product.stock} {product.unit}."
    )



@router.callback_query(
    AdminCallback.filter(F.action == "toggle_active")
)
async def toggle_active_product(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    user: FromDishka[User],
    product_repo: FromDishka[ProductRepository],
):
    if not user.is_admin:
        await callback.answer(
            "⛔️ Доступ запрещён",
            show_alert=True,
        )
        return
    product_id = callback_data.product_id
    product = await product_repo.get_by_id(product_id)
    if not product: 
        return 
    product.is_active = not product.is_active
    product = await product_repo.save(product)
    await callback.message.edit_reply_markup(
        reply_markup=admin_product_keyboard(product)
    )



@router.callback_query(
    AdminCallback.filter(F.action == CallbackAction.ALL_NOT_COMPLETE_ORDERS)
)
async def get_all_orders(
    callback: CallbackQuery,
    order_repo: FromDishka[OrderRepository]
):
    orders = await order_repo.get_all_created_orders()
    if not orders:
        await callback.answer(
            "Заказов пока нет"
        )
        return 
    
    await callback.message.delete()
    
    for order in orders:
        await callback.message.answer(
            admin_order_formatter(order),
            reply_markup=admin_order_keyboard(order)
        )

@router.callback_query(
    AdminCallback.filter(F.action == CallbackAction.ALL_COMPLETE_ORDERS)
)
async def get_all_orders(
    callback: CallbackQuery,
    order_repo: FromDishka[OrderRepository]
):
    orders = await order_repo.get_all_complete_orders()
    if not orders:
        await callback.answer(
            "Заказов пока нет"
        )
        return 
    
    await callback.message.delete()
    
    for order in orders:
        await callback.message.answer(
            admin_order_formatter(order),
        )


@router.callback_query(
    AdminOrderCallback.filter(F.action == CallbackAction.COMPLETE_ORDER)
)
@inject
async def complete_order(
    callback: CallbackQuery,
    callback_data: AdminOrderCallback,
    bot: FromDishka[Bot],
    order_repo: FromDishka[OrderRepository],
): 
    order = await order_repo.get_by_id(callback_data.order_id)
    if not order:
        return 
    await bot.send_message(
        chat_id=order.user.telegram_id,
        text="Ваш заказ доставлен"
    )
    await bot.send_message(
        chat_id=order.user.telegram_id,
        text=order_formatter(order).as_html()
    )
    order.status = OrderStatus.completed
    for item in order.products:
        item.product.stock -= item.quantity
    
    await order_repo.save(order)
    await callback.message.delete()

@router.callback_query(
    AdminOrderCallback.filter(F.action == CallbackAction.CANCEL_ORDER)
)
@inject
async def cancel_order(
    callback: CallbackQuery,
    callback_data: AdminOrderCallback,
    bot: FromDishka[Bot],
    order_repo: FromDishka[OrderRepository]
): 
    order = await order_repo.get_by_id(callback_data.order_id)
    if not order:
        return 
    await bot.send_message(
        chat_id=order.user.telegram_id,
        text="Ваш заказ отменен"
    )
    await bot.send_message(
        chat_id=order.user.telegram_id,
        text=order_formatter(order).as_html()
    )
    order.status = OrderStatus.cancelled
    await order_repo.save(order)
    await callback.message.delete()


@router.callback_query(
    AdminCallback.filter(F.action == CallbackAction.DELETE)
)
async def delete_product(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    product_repo: FromDishka[ProductRepository],
):
    try:
        await product_repo.soft_delete(callback_data.product_id)
    except ValueError:
        await callback.message.answer("Нельзя удалить активный товар") 
        return
    await callback.message.delete()
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from dishka.integrations.aiogram import FromDishka
from src.models.postgres import User
from src.repositories.order_item import OrderProductRepository
from src.bot.callback_data import ProductCallback
from src.enums import MainMenu
from src.repositories import ProductRepository
from src.bot.formaters import product_formatter
from src.bot.keyboards import product_keyboard

router = Router()


@router.message(F.text == MainMenu.CATALOG)
async def catalog(
    message: Message,
    user: FromDishka[User],
    product_repo: FromDishka[ProductRepository],
    order_product_repo: FromDishka[OrderProductRepository]
):
    await message.delete()
    product = await product_repo.get_first()
    if not product: 
        await message.answer("🛍 Каталог пока пуст.")
        return
    quantity_in_cart = await order_product_repo.get_quantity_in_cart(
        user_id=user.id,
        product_id=product.id
    )
    await message.answer_photo(
        photo=FSInputFile(product.preview),
        caption=product_formatter(product),
        reply_markup=product_keyboard(product.id, quantity_in_cart),
    )



@router.callback_query(ProductCallback.filter(F.action == "next"))
async def next_product(
    callback: CallbackQuery,
    callback_data: ProductCallback,
    user: FromDishka[User],
    product_repo: FromDishka[ProductRepository],
    order_product_repo: FromDishka[OrderProductRepository]
):
    product = await product_repo.get_next(callback_data.product_id)

    if not product:
        await callback.answer("Последний товар")
        return
    
    quantity_in_cart = await order_product_repo.get_quantity_in_cart(
        user_id=user.id,
        product_id=product.id
    )

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(product.preview),
            caption=product_formatter(product),
        ),
        reply_markup=product_keyboard(product.id, quantity_in_cart),
    )

    await callback.answer()


@router.callback_query(ProductCallback.filter(F.action == "prev"))
async def prev_product(
    callback: CallbackQuery,
    callback_data: ProductCallback,
    user: FromDishka[User],
    product_repo: FromDishka[ProductRepository],
    order_product_repo: FromDishka[OrderProductRepository]
):
    product = await product_repo.get_previous(callback_data.product_id)

    if not product:
        await callback.answer("Первый товар")
        return
    quantity_in_cart = await order_product_repo.get_quantity_in_cart(
        user_id=user.id,
        product_id=product.id
    )
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(product.preview),
            caption=product_formatter(product),
        ),
        reply_markup=product_keyboard(product.id, quantity_in_cart),
    )

    await callback.answer()
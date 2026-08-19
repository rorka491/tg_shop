from uuid import UUID

from aiogram.types import CallbackQuery
from src.bot.keyboards import product_keyboard
from src.enums import OrderStatus
from src.repositories import OrderProductRepository, ProductRepository, OrderRepository
from src.models.postgres import User


class AddToOrderCommand:
    def __init__(
        self,
        user: User,
        order_repo: OrderRepository,
        order_product_repo: OrderProductRepository,
        product_repo: ProductRepository,
    ) -> None:
        self.user = user
        self.order_repo = order_repo
        self.order_product_repo = order_product_repo
        self.product_repo = product_repo

    
    async def execute(self, product_id: UUID, callback: CallbackQuery):
        product = await self.product_repo.get_by_id(product_id)

        if product is None:
            raise ValueError("Product not found")

        if not product.is_active:
            raise ValueError("Product is not active")

        if product.stock <= 0:
            await callback.answer("товар закончился")
            return

        order = await self.order_repo.get_pending_by_user_id(self.user.id)

        if order is None:
            order = await self.order_repo.create(
                user_id=self.user.id,
                status=OrderStatus.pending,
                total_price=0,
            )

        item = await self.order_product_repo.get_by_order_and_product(
            order.id,
            product.id,
        )

        if item is None:
            item = await self.order_product_repo.create(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                price=product.price,
            )
        else:
            if item.quantity >= product.stock:
                await callback.answer("товар закончился")
                return

            item.quantity += 1
            await self.order_product_repo.save(item)

        order.total_price += product.price
        await self.order_repo.save(order)
        await callback.message.edit_reply_markup(
            reply_markup=product_keyboard(
                product.id,
                quantity_in_cart=item.quantity,
            )
        )


class RemoveFromOrderCommand:

    def __init__(
        self,
        user: User,
        order_repo: OrderRepository,
        order_product_repo: OrderProductRepository,
        product_repo: ProductRepository,
    ) -> None:
        self.user = user
        self.order_repo = order_repo
        self.order_product_repo = order_product_repo
        self.product_repo = product_repo

    async def execute(self, product_id: UUID, callback: CallbackQuery):
        product = await self.product_repo.get_by_id(product_id)

        if product is None:
            raise ValueError("Product not found")

        if not product.is_active:
            raise ValueError("Product is not active")

        order = await self.order_repo.get_pending_by_user_id(self.user.id)

        if order is None:
            return 

        item = await self.order_product_repo.get_by_order_and_product(
            order.id,
            product.id,
        )

        if item is None:
            return
        
        if item.quantity == 1:
            quantity_in_cart = 0
            order.products.remove(item)
        else:
            item.quantity -= 1
            quantity_in_cart = item.quantity

        order.total_price -= product.price
        await self.order_repo.save(order)
        await callback.message.edit_reply_markup(
            reply_markup=product_keyboard(
                product.id,
                quantity_in_cart=quantity_in_cart,
            )
        )

class ClearCartCommand:

    def __init__(
        self,
        user: User,
        order_repo: OrderRepository,
    ) -> None:
        self.user = user
        self.order_repo = order_repo

    async def execute(self, callback: CallbackQuery):
        order = await self.order_repo.get_pending_by_user_id(
            self.user.id,
        )

        if order is None:
            return
        order.products.clear()
        order.total_price = 0

        await self.order_repo.save(order)
        await callback.message.edit_text(
            "🛒 <b>Корзина пуста</b>",
            parse_mode="HTML",
        )
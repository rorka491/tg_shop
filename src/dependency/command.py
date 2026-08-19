from aiogram.types import CallbackQuery
from dishka import Provider, Scope, provide
from src.models.postgres import User
from src.repositories.order import OrderRepository
from src.repositories.order_item import OrderProductRepository
from src.repositories.product import ProductRepository
from src.bot.commands import AddToOrderCommand, ClearCartCommand, RemoveFromOrderCommand


class CommandProvider(Provider):

    @provide(scope=Scope.REQUEST)
    async def add_to_cart(
        self, 
        user: User,
        order_repo: OrderRepository,
        order_product_repo: OrderProductRepository,
        product_repo: ProductRepository,
    ) -> AddToOrderCommand:
        return AddToOrderCommand(
            user=user,
            order_repo=order_repo,
            order_product_repo=order_product_repo,
            product_repo=product_repo
        )

    @provide(scope=Scope.REQUEST)
    async def remove_from_cart(
        self, 
        user: User,
        order_repo: OrderRepository,
        order_product_repo: OrderProductRepository,
        product_repo: ProductRepository,
    ) -> RemoveFromOrderCommand:
        return RemoveFromOrderCommand(
            user=user,
            order_repo=order_repo,
            order_product_repo=order_product_repo,
            product_repo=product_repo
        )

    @provide(scope=Scope.REQUEST)
    async def clear_cart(
        self,
        user: User,
        order_repo: OrderRepository,
    ) -> ClearCartCommand:
        return ClearCartCommand(
            user=user,
            order_repo=order_repo
        )
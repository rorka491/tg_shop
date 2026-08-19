from dishka import Provider
from src.models.postgres import User, Product, OrderProduct, Order


class ModelProvider(Provider):

    def user(self) -> type[User]:
        return User

    def product(self) -> type[Product]:
        return Product

    def order(self) -> type[Order]:
        return Order

    def order_item(self) -> type[OrderProduct]:
        return OrderProduct

    # def payment(self) -> type[Payment]:
    #     return Payment
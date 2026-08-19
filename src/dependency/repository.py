from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from src.repositories.service_password import ServicePasswordRepository
from src.models.postgres import User, Order, OrderProduct, Product
from src.repositories import UserRepository, ProductRepository, OrderProductRepository, OrderRepository

class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    def service_password_repository(self, redis: Redis) -> ServicePasswordRepository:
        return ServicePasswordRepository(redis=redis)

    @provide(scope=Scope.REQUEST)
    def user_repository(
        self,
        session: AsyncSession,
        model: type[User],
    ) -> UserRepository:
        return UserRepository(session, model)

    @provide(scope=Scope.REQUEST)
    def product_repository(
        self,
        session: AsyncSession,
        model: type[Product],
    ) -> ProductRepository:
        return ProductRepository(session, model)

    @provide(scope=Scope.REQUEST)
    def order_repository(
        self,
        session: AsyncSession,
        model: type[Order],
    ) -> OrderRepository:
        return OrderRepository(session, model)

    @provide(scope=Scope.REQUEST)
    def order_product_repository(
        self,
        session: AsyncSession,
        model: type[OrderProduct],
    ) -> OrderProductRepository:
        return OrderProductRepository(session, model)

    # @provide(scope=Scope.REQUEST)
    # def payment_repository(
    #     self,
    #     session: AsyncSession,
    #     model: type[Payment],
    # ) -> PaymentRepository:
    #     return PaymentRepository(session, model)
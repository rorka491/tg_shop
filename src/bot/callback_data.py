from uuid import UUID
from aiogram.filters.callback_data import CallbackData


class CartCallback(CallbackData, prefix="cart"):
    action: str
    product_id: UUID | None = None

class ProductCallback(CallbackData, prefix="product"):
    action: str
    product_id: UUID

class AdminCallback(CallbackData, prefix="admin"):
    action: str
    product_id: UUID | None = None


class OrderCallback(CallbackData, prefix="order"):
    action: str
    order_id: UUID | None = None

class AdminOrderCallback(CallbackData, prefix="admin_order"):
    action: str
    order_id: UUID
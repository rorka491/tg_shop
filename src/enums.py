from enum import StrEnum


class OrderStatus(StrEnum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"
    completed = "completed"


class MainMenu(StrEnum):
    CATALOG = "🛍 Каталог"
    CART = "🛒 Корзина"
    ORDERS = "📦 Заказы"
    PROFILE = "👤 Профиль"
    HELP = "ℹ️ Помощь"


from enum import StrEnum


class CallbackAction(StrEnum):
    # product
    PREV = "prev"
    NEXT = "next"

    # cart
    ADD = "add"
    REMOVE = "remove"
    CLEAR = "clear"
    ORDER = "order"

    # order
    SELF_PICKUP = "self_pickup"
    DELIVERY = "delivery"
    ALL_COMPLETE_ORDERS = "all_complete_orders"
    ALL_NOT_COMPLETE_ORDERS = "all_not_complete_orders"
    CONFIRM_ORDER = "confirm_order"

    # admin
    COMPLETE_ORDER = "complete_order"
    CANCEL_ORDER = "cancel_order"
    NOMENCLATURE = "nomenclature"
    STOCK = "stock"
    PRICE = "price"
    EDIT = "edit"
    TOGGLE_ACTIVE = "toggle_active"
    DELETE = "delete"
from uuid import UUID
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


from src.models.postgres import Product, Order
from src.bot.callback_data import AdminCallback, AdminOrderCallback, CartCallback, OrderCallback, ProductCallback
from src.enums import MainMenu, CallbackAction

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=MainMenu.CATALOG)],
        [
            KeyboardButton(text=MainMenu.CART),
            KeyboardButton(text=MainMenu.ORDERS),
        ],
    ],
    resize_keyboard=True,
)


def order_type_keyboard(order: Order):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Самовывоз",
                    callback_data=OrderCallback(
                        action=CallbackAction.SELF_PICKUP,
                        order_id=order.id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Доставка",
                    callback_data=OrderCallback(
                        action=CallbackAction.DELIVERY,
                        order_id=order.id,
                    ).pack(),
                ),
            ],   
        ]
    )


def admin_order_keyboard(order: Order) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Завершить",
                    callback_data=AdminOrderCallback(
                        action=CallbackAction.COMPLETE_ORDER,
                        order_id=order.id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=AdminOrderCallback(
                        action=CallbackAction.CANCEL_ORDER,
                        order_id=order.id,
                    ).pack(),
                ),
            ],
        ]
    )


def product_keyboard(product_id: UUID, quantity_in_cart: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=ProductCallback(
                        action=CallbackAction.PREV,
                        product_id=product_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=ProductCallback(
                        action=CallbackAction.NEXT,
                        product_id=product_id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"✅ В корзину ({quantity_in_cart})",
                    callback_data=CartCallback(
                        action=CallbackAction.ADD,
                        product_id=product_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Убрать",
                    callback_data=CartCallback(
                        action=CallbackAction.REMOVE,
                        product_id=product_id,
                    ).pack(),
                ),
            ]
        ]
    )



def cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Заказать",
                    callback_data=CartCallback(action=CallbackAction.ORDER).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Очистить корзину",
                    callback_data=CartCallback(action=CallbackAction.CLEAR).pack(),
                ),
            ],
        ]
    )



def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Заказы",
                    callback_data=AdminCallback(action=CallbackAction.ALL_ORDERS).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📦 Номенклатура",
                    callback_data=AdminCallback(action=CallbackAction.NOMENCLATURE).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить товар",
                    callback_data=AdminCallback(action=CallbackAction.ADD).pack(),
                ),
            ],
        ]
    )


def admin_product_keyboard(
    product: Product,
) -> InlineKeyboardMarkup:

    is_active_text = "🔴 Деактивирован"
    if product.is_active:
        is_active_text = "🟢 Активен"
        
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Изменить остаток",
                    callback_data=AdminCallback(
                        action=CallbackAction.STOCK,
                        product_id=product.id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💰 Изменить цену",
                    callback_data=AdminCallback(
                        action=CallbackAction.PRICE,
                        product_id=product.id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=is_active_text,
                    callback_data=AdminCallback(
                        action=CallbackAction.TOGGLE_ACTIVE,
                        product_id=product.id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=AdminCallback(
                        action=CallbackAction.DELETE,
                        product_id=product.id,
                    ).pack(),
                ),
            ],
        ]
    )


def pickup_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=OrderCallback(
                        action=CallbackAction.CONFIRM_ORDER,
                    ).pack(),
                ),
            ],
            # [
            #     InlineKeyboardButton(
            #         text="🔄 Изменить дату и время",
            #         callback_data=OrderCallback(
            #             action=CallbackAction.CHANGE_DATE_TIME,
            #         ).pack(),
            #     ),
            # ],
        ]
    )




location_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📍 Отправить геопозицию",
                request_location=True,
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
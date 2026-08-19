from src.models.postgres import Product, Order
from aiogram.utils.formatting import (
    Bold,
    Text,
)
from html import escape
from src.enums import OrderStatus


def product_formatter(product: Product) -> str:
    return (
            f"{product.name}\n"
            f"💰 {product.price} ₽\n\n"
             f"📦 В наличии: {product.stock} л.\n\n"
            f"{product.description or ''}"
        )




def admin_formatter(service_password: str | None) -> Text:
    return Text(
        Bold("⚙️ Админ-панель"),
        "\n\n",
        "🔐 ",
        Bold("Код доступа:"),
        f" {service_password or 'не установлен'}",
    )


from aiogram.utils.formatting import Text, Bold, as_list

def order_formatter(order: Order) -> Text:
    # Инициализируем список элементов корзины
    product_lines = []

    for index, item in enumerate(order.products, start=1):
        total = item.quantity * item.price

        # Добавляем каждый товар как отдельный объект Text
        product_lines.append(
            Text(
                Bold(f"{index}. {item.product.name}"),
                "\n",
                f"   {item.quantity} шт. × {item.price:.0f} ₽ = ",
                Bold(f"{total:.0f} ₽"),
            )
        )

    # Собираем финальный текст через as_list
    return as_list(
        Text("🛒 ", Bold("Ваша корзина")),
        "",          
        *product_lines,
        "",               
        Text(
            "💰 ",
            Bold("Итого:"),
            f" {order.total_price:.0f} ₽",
        )
    )




def list_order_formatter(orders: list[Order]) -> str:
    if not orders:
        return "📦 <b>У вас пока нет заказов</b>"

    status_map = {
        OrderStatus.pending: "🟡 В обработке",
        OrderStatus.paid: "🟢 Оплачен",
        OrderStatus.completed: "✅ Выполнен",
        OrderStatus.cancelled: "❌ Отменён",
    }

    lines = ["📦 <b>Ваши заказы</b>\n"]

    for index, order in enumerate(orders, start=1):
        status = status_map.get(order.status, str(order.status))

        lines.append(
            f"<b>Заказ #{index}</b>\n"
            f"💰 Сумма: <b>{order.total_price} ₽</b>\n"
            f"📌 Статус: <b>{status}</b>\n"
            f"📅 Создан: "
            f"<b>{order.created_at.strftime('%d.%m.%Y %H:%M')}</b>"
        )

        if order.delivery_address:
            lines.append(
                f"🚚 Доставка: "
                f"<b>{order.delivery_address}</b>"
            )

            if order.delivery_at:
                lines.append(
                    f"🕒 Дата доставки: "
                    f"<b>{order.delivery_at.strftime('%d.%m.%Y %H:%M')}</b>"
                )

        elif order.pickup_at:
            lines.append(
                "🏪 Способ получения: <b>Самовывоз</b>"
            )
            lines.append(
                f"🕒 Дата самовывоза: "
                f"<b>{order.pickup_at.strftime('%d.%m.%Y %H:%M')}</b>"
            )

        if order.products:
            lines.append("\n🛒 <b>Состав заказа:</b>")

            for product in order.products:
                lines.append(
                    f"• {product.product.name} "
                    f"× {product.quantity}"
                )

        lines.append("\n➖➖➖➖➖➖➖➖➖➖\n")

    return "\n".join(lines)



def admin_order_formatter(order: Order) -> str:
    username = (
        f"@{escape(order.user.username)}"
        if order.user.username
        else "без username"
    )

    lines = [
        f"👤 Пользователь: <b>{username}</b>",
        "",
    ]

    for index, item in enumerate(order.products, start=1):
        total = item.quantity * item.price

        lines.extend([
            f"<b>{index}. {escape(item.product.name)}</b>",
            (
                f"   {item.quantity} шт. × "
                f"{item.price:.0f} ₽ = "
                f"<b>{total:.0f} ₽</b>"
            ),
        ])
    if order.delivery_address:
        lines.extend([
            "",
            f"📍 Адрес доставки: {escape(order.delivery_address)}"
        ])

    if order.delivery_at:
        lines.extend([
            "",
            f"🕒 Время доставки: {order.delivery_at}"
        ])

    if order.pickup_at:
        lines.extend([
            "",
            f"🏪 Самовывоз: {order.pickup_at}"
        ])

    lines.extend([

        "",
        f"💰 <b>Итого: {order.total_price:.0f} ₽</b>",
    ])

    return "\n".join(lines)
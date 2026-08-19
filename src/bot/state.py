from aiogram.fsm.state import State, StatesGroup



class BotState(StatesGroup):
    ...


class AddProductState(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    preview = State()

class UpdateProductState(StatesGroup):
    stock = State()
    price = State()


class AccessState(StatesGroup):
    waiting_for_password = State()


class SelfPickUpState(StatesGroup):
    waiting_for_date_time = State()
    waiting_for_confirmation = State()


class DeliveryState(StatesGroup):
    waiting_for_address = State()
    waiting_for_date_time = State()
    waiting_for_confirmation = State()


class ChangePrice(StatesGroup):
    waiting_for_price = State()
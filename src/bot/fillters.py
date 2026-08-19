from aiogram.filters import BaseFilter
from aiogram.types import Message

from enums import MainMenu


class CatalogFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text == MainMenu.CATALOG
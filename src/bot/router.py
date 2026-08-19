from aiogram import Router 
from src.middleware import PermissionMiddleware, TelegramUserMiddleware
from src.bot.handler.start import router as start_router
from src.bot.handler.catalog import router as catalog_router
from src.bot.handler.cart import router as cart_router
from src.bot.handler.admin import router as admin_router
from src.bot.handler.order import router as order_router


router = Router()

router.include_router(start_router)
router.include_router(catalog_router)
router.include_router(cart_router)
router.include_router(admin_router)
router.include_router(order_router)

router.message.middleware(TelegramUserMiddleware())
router.message.middleware(PermissionMiddleware())
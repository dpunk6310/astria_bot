
from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.backend.api import (
    get_user,
    get_price_list
)
from core.logger.logger import get_logger

promo_router = Router()

log = get_logger()


@promo_router.message(F.text == "Подарить Пингвин ИИ")
async def give_pingvin_handler(message: types.Message):
    price_list = await get_price_list("promo")
    builder = InlineKeyboardBuilder()
    price_str = ""
    for i in price_list:
        if i.get("learn_model"):
            continue
        sale = i.get("sale", None)
        builder.button(
            text=f"{i.get('count')} фото",
            callback_data=f"inst_payment_{i.get('price')}_0_{False}_0_{True}_{i.get('count')}"
        )
        log.debug(f"inst_payment_{i.get('price')}_0_{False}_0_{True}_{i.get('count')}")
        if not sale or sale == "":
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽\n"
        else:
            price_str += f"* {i.get('count')} фото: {i.get('price')}₽ ({sale})\n"
    builder.adjust(2, 2, 2)
    text = """
Варианты:
{price_str}
Выберите свой вариант!
""".format(price_str=price_str)
    await message.answer(
        text=text,
        reply_markup=builder.as_markup()
    )


def setup(dp):
    dp.include_router(promo_router)   


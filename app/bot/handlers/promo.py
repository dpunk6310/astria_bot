
from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.backend.api import (
    get_user,
    update_promo,
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
        sale = i.get("sale", None)
        # TODO: Добавить в модель прайс лист кол-во видео генераций для promo
        builder.button(
            text=f"{i.get('count')} фото",
            callback_data=f"inst_payment_{i.get('price')}_0_{i.get('learn_model')}_0_1_{i.get('count')}_{i.get('count_video')}"
        )
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
    
    
@promo_router.message(F.text.contains("PROMO_"))
async def activate_promo_handler(message: types.Message):
    response = await update_promo(data={
        "code": message.text,
        "tg_user_id": str(message.chat.id),
        "status": False,
    })
    if not response or not response.get("code"):
        await message.answer(text="Такого промода не существует, либо он уже активирован 😕")
        return
    # code = response.get("code")
    # status = response.get("status")
    count_generations = response.get("count_generations")
    count_video_generations = response.get("count_video_generations")
    is_learn_model = bool(response.get("is_learn_model"))
    
    help_text = f"{count_generations} фото, {count_video_generations} оживление"
    if is_learn_model:
        help_text = f"{count_generations} фото, 1 аватар, {count_video_generations} оживление"
    if count_video_generations == 0:
        help_text = f"{count_generations} фото, 1 аватар"
    if not is_learn_model and count_video_generations == 0:
        help_text = f"{count_generations} фото"
    await message.answer(
        text="""<b>Ваш промокод успешно активирован!</b> 🐧

Вам начислено:

{help_text}
""".format(help_text=help_text), parse_mode="HTML"
    )


def setup(dp):
    dp.include_router(promo_router)   


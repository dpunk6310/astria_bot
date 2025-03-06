from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from core.backend.api import (
    get_user,
)
from core.logger.logger import get_logger


referal_router = Router()
log = get_logger()

    
@referal_router.message(F.text == "Партнёрская программа")
async def referal_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_db = await get_user(str(message.chat.id))
    await message.answer(
        text="""
<b>Зарабатывай вместе с нашим ботом!</b>

<b>Мы подарим 20 генераций</b> за каждого, кто оплатит доступ к Пингвин ии  ❤️🖖

<b>Реферальная статистика:</b> 

Количество рефералов:  {referral_count}

Ваше вознаграждение:  {reward_generations} фото

Сколько сделали покупок: {referral_purchases} 

🔗<b> Ваша реферальная ссылка:</b>  https://t.me/photopingvin_bot?start={chat_id}
""".format(
        referral_count=user_db.get("referral_count"), 
        reward_generations=user_db.get("reward_generations"),
        referral_purchases=user_db.get("referral_purchases"),
        chat_id=message.chat.id
    ),
        parse_mode="HTML"
    )
    

def setup(dp):
    dp.include_router(referal_router)    

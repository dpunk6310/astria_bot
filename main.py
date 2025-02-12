import httpx


def send_message_successfully_pay(bot_token: str, chat_id: str, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = httpx.post(url=url, json=payload)
        return response.json()
    except Exception as e:
        return {"err": str(e)}


send_message_successfully_pay(
    bot_token="7840314780:AAEnowO22AigiBvKNwYZDL-H2e3N-amGI_g",
    chat_id="758103378",
    text="""
❗️ <b>Уважаемые пользователи!</b>❗️

Предупреждаем Вас, что через 30 минут мы проведем технические работы по боту - в это время бот может не работать

Пожалуйста, не используйте бота в это время - генерация, оплата и другие функции могут не работать

Мы пришлем уведомление как технические работы начнуться и завершаться ❤️
    """
)

send_message_successfully_pay(
    bot_token="7840314780:AAEnowO22AigiBvKNwYZDL-H2e3N-amGI_g",
    chat_id="758103378",
    text="""
❗️ <b>Уважаемые пользователи!</b>❗️

По боту начались плановые технические работы

Убедительно просим Вас не использоваться бота в это время - так как основные функции временно работать не будут

Это займет немного времени. Мы пришлем уведомление как технические работы завершаться ❤️
    """
)

send_message_successfully_pay(
    bot_token="7840314780:AAEnowO22AigiBvKNwYZDL-H2e3N-amGI_g",
    chat_id="758103378",
    text="""
❗️ <b>Уважаемые пользователи!</b>❗️

Технические работы завершены. Бот работает стабильно

В случае возникновения каких-либо проблем вы можете связать с поддержкой через кнопку "Служба поддержки"

Приносим извенения за доставленные неудобства. Мы рады, что Вы с нами ❤️
    """
)
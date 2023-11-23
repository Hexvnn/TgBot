import os
import time

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

load_dotenv()
secret_token = os.getenv("TOKEN")


def send_welcome_message(update: Update, context: CallbackContext):
    context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open("logo/logo.jpg", "rb")
    )
    username = update.message.from_user.first_name
    welcome_message = f"Привет, {username}! Добро пожаловать в наш магазин! 🎉\nТы попал в нашего бота, в котором можно быстро узнать цену на товар или оформить заказ без очереди 😉"
    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 Основной канал", url="https://t.me/seller_username"
            ),
            InlineKeyboardButton(
                "📩 Отзывы о нас",
                url="https://t.me/reviews_channel",
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup)
    send_main_menu(update, context)


def send_main_menu(update, context, reply_markup=None):
    custom_keyboard = [["💸 Заказ/Цена", "🎁 Акция", "💎 Инфо"]]
    reply_markup = (
        reply_markup
        if reply_markup is not None
        else ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    )
    update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


def send_promotion_message(update, context):
    promotion_text = """
    Всем привет, друзья !

    С 07.11 по 09.11 У нас скидки на доставку до Москвы
    Доставка футболок/худи - 250р
    Доставка обуви - 700р
    Доставка курток/верхней одежды - 500р

    И у каждого из вас будет шанс опробовать Экспресс доставку абсолютно бесплатно 😘

    Посылка экспресс доедет до Москвы буквально за 3-5 дней, с момента оформления заказа

    Ждем 10-11 числа, будет самый жир
    """
    context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open("action/Акция.jpg", "rb")
    )
    reply_markup = ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
    update.message.reply_text(promotion_text, reply_markup=reply_markup)


def send_info_message(update, context):
    info_text = """
    Наши условия для заказа:

    Стоимость доставки 1 пары кроссовок - примерно 1600 Р с учетом СДЕКА
    Стоимость доставки одежды - примерно 700 Р с учетом СДЕКА
    (Финальная стоимость доставки будет известна, когда товар будет взвешен на нашем складе)
    Если товар не подошел - мы можем помочь вам продать его, либо заказать аналогичный, но с хорошей скидкой.

    Расценки на заказ:
    От 100 до 500 ¥ - 800 рублей
    От 501 до 1000 ¥ - 9% от суммы товара
    От 1001-2000 ¥- 8% от суммы товара
    От 2001 ¥ - 7% от суммы товара

    Примерную стоимость доставки вы можете узнать в нашем боте.

    Заказ будет обработан в течение часа, с нашей стороны мы предоставим скриншот покупки, от вас нам потребуется ФИО, Город, Адрес СДЭКА и номер телефона

    Если у вас остались вопросы, можете задать их здесь → @dabiks
    """
    reply_markup = ReplyKeyboardMarkup([["⬅️ Назад"]], resize_keyboard=True)
    update.message.reply_text(info_text, reply_markup=reply_markup)


def send_order_price_menu(update, context):
    reply_markup = ReplyKeyboardMarkup(
        [["📠 Узнать цену", "🛍 Сделать заказ", "⬅️ Назад"]],
        resize_keyboard=True,
    )
    update.message.reply_text(
        "Выберите нужный вариант",
        reply_markup=reply_markup,
    )


def handle_price_request(update, context):
    update.message.reply_text("Введите стоимость желаемого товара (в ¥ Юанях)")
    context.user_data["expecting_price_input"] = True


def handle_price_response(update, context):
    user_input = update.message.text
    if user_input.replace(".", "", 1).isdigit():
        amount_in_yuan = float(user_input)
        exchange_rate = 12.3
        amount_in_rubles = int(amount_in_yuan * exchange_rate)
        response_text = f"Итого {amount_in_rubles} рублей"
        reply_markup = ReplyKeyboardMarkup(
            [["⬅️ Назад"]],
            resize_keyboard=True,
        )
        update.message.reply_text(response_text, reply_markup=reply_markup)
        inline_keyboard = [
            [InlineKeyboardButton("📦 Заказать", url="https://t.me/seller_username")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Закажи этот товар у нас",
            reply_markup=inline_markup,
        )


def handle_order_request(update, context):
    message = "⚠️ Нужна инструкция"
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="yes_instruction"),
            InlineKeyboardButton("Нет", callback_data="no_instruction"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)


def handle_instruction_response(update, context):
    message = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🚛 Написать продавцу", url="http://t.me/username_seller"
                )
            ]
        ]
    )

    query = update.callback_query
    context.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id, message_id=query.message.message_id
    )
    if query.data == "yes_instruction":
        send_instruction_steps(query.message.chat_id, context)
    else:
        query.message.reply_text(
            "✅ Вы разберетесь без нашей инструкции\n\nОтправьте ссылку на товар продавцу",
            reply_markup=message,
        )


def send_instruction_steps(chat_id, context):
    messages = [
        "1/7 Для того, чтобы бот правильно посчитал цену, выберите нужный товар, затем нажмите на кнопку, указанную ниже",
        "2/7 Далее выберите нужный вам размер (1.) и нажмите на кнопку ниже(2.). Если потребуется размерная сетка, то она находится выше (3.)",
        "3/7 На скриншоте представлена цена, которую нужно написать боту, чтобы он посчитал цену с учетом комиссии.",
        "4/7 Внимание! Иногда цена сверху, может быть больше, чем снизу, тогда мы считаем по той, которая находится сверху, связано это с тем, что у вас имеются активированные промокоды, но у нас их нет, поэтому выкупаем без их учета.",
        "5/7 Предупреждаем! В приложении имеются товары, перед ценой у которых стоит волнистая черта, или может быть именно у вашего размера стоит волнистая черта, это означает, что товар находится не в Китае. Такой товар мы доставим, но сроки доставки немного увеличатся, примерный срок доставки будет написан на кнопке (До склада в Китае). Рассчитывается он так же, как на примере выше.",
        "6/7 Если вам понадобится ссылка на товар, то она находится в правом верхнем углу. (Иногда она принимает вид зелёного значка ВиЧата).",
        "7/7 Когда откроется окно, нажмите на указанную кнопку ниже, далее ссылка на товар будет скопирована. После этого отправьте ее нам в личные сообщения. ",
    ]

    seller = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🚛 Написать продавцу", url="http://t.me/username_seller"
                )
            ]
        ]
    )

    for i, message in enumerate(messages, start=1):
        photo_path = f"images/{i}.jpg"
        with open(photo_path, "rb") as photo:
            context.bot.send_photo(chat_id=chat_id, photo=photo)
        if i == len(messages):
            context.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=seller,
            )
        else:
            context.bot.send_message(chat_id=chat_id, text=message)
        time.sleep(3)


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "/start":
        send_welcome_message(update, context)
    elif text == "💎 Инфо":
        send_info_message(update, context)
    elif text == "🎁 Акция":
        send_promotion_message(update, context)
    elif text == "💸 Заказ/Цена":
        send_order_price_menu(update, context)
    elif text == "📠 Узнать цену":
        handle_price_request(update, context)
    elif text == "🛍 Сделать заказ":
        handle_order_request(update, context)
    elif text == "⬅️ Назад":
        send_main_menu(update, context)
    else:
        if context.user_data.get("expecting_price_input", False):
            handle_price_response(update, context)
            context.user_data["expecting_price_input"] = False


def main():
    updater = Updater(secret_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", send_welcome_message))
    dp.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            handle_message,
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            handle_instruction_response,
            pattern="yes_instruction",
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            handle_instruction_response,
            pattern="no_instruction",
        )
    )
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

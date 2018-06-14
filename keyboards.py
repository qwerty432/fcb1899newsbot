from telebot import types
import parse


def set_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Следующий матч')
    keyboard.row('Новости')
    keyboard.row('Время')
    keyboard.row('Настройки')
    return keyboard


def set_return_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Назад')
    return keyboard


def set_news_buttons():
    keyboard = types.InlineKeyboardMarkup()

    news = parse.parse_latest_news()
    titles = news['titles']
    for i, title in enumerate(titles) :
        button = types.InlineKeyboardButton(
                                    text=title,
                                    callback_data="button{}".format(i))
        keyboard.add(button)

    return keyboard

from telebot import types
import parse
import users_controller


def set_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Последний матч', 'Следующий матч')
    keyboard.row('Время', 'Состав')
    keyboard.row('Новости')
    keyboard.row('Настройки')
    return keyboard


def set_return_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Назад')
    return keyboard


def set_news_buttons(user_id):
    keyboard = types.InlineKeyboardMarkup()

    news = parse.parse_news(user_id)
    titles = news['titles']
    users_controller.set_urls(user_id, news['urls'])
    for i, title in enumerate(titles) :
        button = types.InlineKeyboardButton(
                                    text=title,
                                    callback_data="button{}".format(i))
        keyboard.add(button)

    return keyboard


def set_settings_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)

    keyboard.row('Выбрать команду')
    keyboard.row('Назад')
    return keyboard


def set_teams_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)

    teams = parse.get_teams_list()

    for i, team in enumerate(teams):
        keyboard.row(team)
    keyboard.row('Назад')

    return keyboard

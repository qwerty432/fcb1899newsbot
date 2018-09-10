from telebot import types
import parse
import users_controller
from useful_dictionaries import *


def set_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Последний матч', 'Следующий матч')
    keyboard.row('Время', 'Состав')
    keyboard.row('Новости', 'Статьи')
    keyboard.row('Настройки')
    return keyboard


def set_return_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Назад')
    return keyboard


def set_news_buttons(news):
    keyboard = types.InlineKeyboardMarkup()
    titles = news['titles']
    # users_controller.set_urls(user_id, news['urls'])
    for i, title in enumerate(titles) :
        button = types.InlineKeyboardButton(
                                    text=title,
                                    callback_data="button{}".format(i))
        keyboard.add(button)

    return keyboard


def set_articles_buttons(user_id):
    keyboard = types.InlineKeyboardMarkup()

    articles = parse.parse_articles(user_id)
    titles = articles['titles']
    users_controller.set_urls(user_id, articles['urls'])
    for i, title in enumerate(titles):
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


def set_champs_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)

    for i, team in enumerate(sorted(CHAMPIONATS_DICT.keys())):
        keyboard.row(team)
    keyboard.row('Назад')

    return keyboard


def set_teams_keyboard():
    keyboard = types.ReplyKeyboardMarkup(True)

    teams = parse.get_teams_list()

    for i, team in enumerate(teams):
        keyboard.row(team)
    keyboard.row('Назад')

    return keyboard

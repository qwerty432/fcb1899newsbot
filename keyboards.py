from telebot import types
import parse
import users_controller
from useful_dictionaries import *
from languages import LANG_DICT


def set_main_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row(LANG_DICT[lang]['last_match_btn'], LANG_DICT[lang]['next_match_btn'])
    keyboard.row(LANG_DICT[lang]['time_btn'], LANG_DICT[lang]['squad_btn'])
    keyboard.row(LANG_DICT[lang]['news_btn'], LANG_DICT[lang]['articles_btn'])
    keyboard.row(LANG_DICT[lang]['settings_btn'])
    return keyboard


def set_return_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row(LANG_DICT[lang]['return_btn'])
    return keyboard


def set_news_buttons(user_id, news):
    keyboard = types.InlineKeyboardMarkup()
    titles = news['titles']
    users_controller.set_urls(user_id, news['urls'])
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


def set_settings_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(True)

    keyboard.row(LANG_DICT[lang]['change_lang_btn'])
    keyboard.row(LANG_DICT[lang]['choose_team_btn'])
    keyboard.row(LANG_DICT[lang]['notifications_btn'])
    keyboard.row(LANG_DICT[lang]['return_btn'])
    return keyboard


def set_champs_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(True)

    for i, team in enumerate(sorted(CHAMPIONATS_DICT[lang].keys())):
        keyboard.row(team)
    keyboard.row(LANG_DICT[lang]['return_btn'])

    return keyboard


def set_teams_keyboard(lang, user_id):
    keyboard = types.ReplyKeyboardMarkup(True)

    teams = parse.get_teams_list(user_id)

    for i, team in enumerate(teams):
        keyboard.row(team)
    keyboard.row(LANG_DICT[lang]['return_btn'])

    return keyboard


def set_notifications_keyboard(lang, user_id):
    keyboard = types.ReplyKeyboardMarkup(True)

    keyboard.row(LANG_DICT[lang]['return_btn'])

    return keyboard

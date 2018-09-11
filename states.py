import users_controller
import keyboards
import parse
from useful_dictionaries import *


class States(object):
    def __init__(self, bot):
        self.bot = bot
        self.states = {'start': self.start_state, 'settings_state': self.settings_state,
                       'choose_team_state': self.choose_team_state, 'choose_champ_state': self.choose_champ_state
                       }

    def handle_states(self, message, first_entry=False):
        user = users_controller.get_user(message.chat.id)
        if user is None:
            users_controller.create_user(message)
            user = users_controller.get_user(message.chat.id)

        self.states[user['state']](message, first_entry)

    def go_to_state(self, message, state_name):
        users_controller.update_state(message.chat.id, state_name)
        self.states[state_name](message, first_entry=True)

    def start_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, 'Hello there!',
                                  reply_markup=keyboards.set_main_keyboard())
        else:
            if message.text == 'Следующий матч':
                self.bot.send_message(message.chat.id,
                                      parse.parse_info(users_controller.get_user(message.chat.id)),
                                      parse_mode='markdown')
            elif message.text == 'Последний матч':
                self.bot.send_message(message.chat.id,
                                      parse.parse_info(users_controller.get_user(message.chat.id),
                                                       match_type='last'),
                                      parse_mode='markdown')
            elif message.text == 'Новости':
                parse.send_news(self, message.chat.id)
            elif message.text == 'Статьи':
                parse.send_articles(self, message.chat.id)
            elif message.text == 'Состав':
                self.bot.send_message(message.chat.id, parse.get_teams_squad(message.chat.id),
                                      parse_mode='markdown')
            elif message.text == 'Время':
                self.bot.send_message(message.chat.id, parse.parse_time(users_controller.get_user(message.chat.id)))
            elif message.text == 'Настройки':
                self.go_to_state(message, 'settings_state')
            else:
                self.bot.send_message(message.chat.id, 'Hello there!',
                                      reply_markup=keyboards.set_main_keyboard())

    def settings_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, 'Меню настроек',
                                  reply_markup=keyboards.set_settings_keyboard())
        else:
            if message.text == 'Выбрать команду':
                self.go_to_state(message, 'choose_champ_state')
            elif message.text == 'Назад':
                self.go_to_state(message, 'start')
            else:
                self.go_to_state(message, 'settings_state')

    def choose_champ_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, 'Выберите чемпионат:',
                                  reply_markup=keyboards.set_champs_keyboard())
        else:
            if message.text in CHAMPIONATS_DICT.keys():
                users_controller.set_champ(message.chat.id, message.text)
                self.go_to_state(message, 'choose_team_state')
            elif message.text == 'Назад':
                self.go_to_state(message, 'settings_state')
            else:
                self.go_to_state(message, 'choose_champ_state')

    def choose_team_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, 'Выберите команду:',
                                  reply_markup=keyboards.set_teams_keyboard(message.chat.id))
        else:
            if message.text in parse.get_teams_list(message.chat.id):
                users_controller.set_team(message.chat.id, message.text)
                self.go_to_state(message, 'start')
            elif message.text == 'Назад':
                self.go_to_state(message, 'settings_state')
            else:
                self.go_to_state(message, 'choose_team_state')

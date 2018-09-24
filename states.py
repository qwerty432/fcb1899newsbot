import users_controller
import keyboards
import parse
from useful_dictionaries import CHAMPIONATS_DICT
from languages import LANG_DICT
import bot_methods


class States(object):
    def __init__(self, bot):
        self.bot = bot
        self.states = {'start': self.start_state,
                       'settings_state': self.settings_state,
                       'choose_team_state': self.choose_team_state,
                       'choose_champ_state': self.choose_champ_state,
                       'notifications_state': self.notifications_state
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
        user = users_controller.get_user(message.chat.id)
        lang = user['language']
        if first_entry:
            self.bot.send_message(message.chat.id, LANG_DICT[lang]['hello_msg'],
                                  reply_markup=keyboards.set_main_keyboard(lang))
            if not user.team:
                self.bot.send_message(message.chat.id, LANG_DICT[lang]['first_choose_team_msg'])
                self.go_to_state(message, 'choose_champ_state')
            else:
                pass
        else:
            if message.text == LANG_DICT[lang]['next_match_btn']:
                self.bot.send_message(message.chat.id,
                                      bot_methods.get_match_info(users_controller.get_user(message.chat.id), lang),
                                      parse_mode='markdown')

            elif message.text == LANG_DICT[lang]['last_match_btn']:
                self.bot.send_message(message.chat.id,
                                      bot_methods.get_match_info(users_controller.get_user(message.chat.id), lang,
                                                       match_type='last'),
                                      parse_mode='markdown')

            elif message.text == LANG_DICT[lang]['news_btn']:
                parse.send_news(self, message.chat.id, user.language)

            elif message.text == LANG_DICT[lang]['articles_btn']:
                parse.send_articles(self, message.chat.id, user.language)

            elif message.text == LANG_DICT[lang]['squad_btn']:
                self.bot.send_message(message.chat.id, parse.get_teams_squad(message.chat.id),
                                      parse_mode='markdown')

            elif message.text == LANG_DICT[lang]['time_btn']:
                self.bot.send_message(message.chat.id, parse.parse_time(users_controller.get_user(message.chat.id)))

            elif message.text == LANG_DICT[lang]['settings_btn']:
                self.go_to_state(message, 'settings_state')
            else:
                self.bot.send_message(message.chat.id, LANG_DICT[lang]['hello_msg'],
                                      reply_markup=keyboards.set_main_keyboard(lang))

    def settings_state(self, message, first_entry=False):
        user = users_controller.get_user(message.chat.id)
        lang = user['language']
        if first_entry:
            self.bot.send_message(message.chat.id, LANG_DICT[lang]['settings_btn'],
                                  reply_markup=keyboards.set_settings_keyboard(lang))
        else:
            if message.text == LANG_DICT[lang]['change_lang_btn']:
                users_controller.set_lang(message.chat.id, lang)
                updated_lang = users_controller.get_user(message.chat.id).language
                bot_methods.update_names(user, updated_lang)
                self.bot.send_message(message.chat.id, LANG_DICT[updated_lang]['changed_lang_msg'])
                self.go_to_state(message, 'settings_state')
            elif message.text == LANG_DICT[lang]['choose_team_btn']:
                self.go_to_state(message, 'choose_champ_state')
            elif message.text == LANG_DICT[lang]['notifications_btn']:
                self.go_to_state(message, 'notifications_state')
            elif message.text == LANG_DICT[lang]['return_btn']:
                self.go_to_state(message, 'start')
            else:
                self.go_to_state(message, 'settings_state')

    def choose_champ_state(self, message, first_entry=False):
        user = users_controller.get_user(message.chat.id)
        lang = user['language']
        if first_entry:
            self.bot.send_message(message.chat.id, LANG_DICT[lang]['choose_champ_msg'],
                                  reply_markup=keyboards.set_champs_keyboard(lang))
        else:
            if message.text in CHAMPIONATS_DICT[lang].keys():
                users_controller.set_champ(message.chat.id, message.text)
                self.go_to_state(message, 'choose_team_state')

            elif message.text == LANG_DICT[lang]['return_btn']:
                self.go_to_state(message, 'settings_state')
            else:
                self.go_to_state(message, 'choose_champ_state')

    def choose_team_state(self, message, first_entry=False):
        user = users_controller.get_user(message.chat.id)
        lang = user['language']
        if first_entry:
            self.bot.send_message(message.chat.id, LANG_DICT[lang]['choose_team_msg'],
                                  reply_markup=keyboards.set_teams_keyboard(lang, message.chat.id))
        else:
            if message.text in parse.get_teams_list(message.chat.id):
                users_controller.set_team(message.chat.id, message.text)
                self.go_to_state(message, 'start')
            elif message.text == LANG_DICT[lang]['return_btn']:
                self.go_to_state(message, 'choose_champ_state')
            else:
                self.go_to_state(message, 'choose_team_state')

    def notifications_state(self, message, first_entry=False):
        user = users_controller.get_user(message.chat.id)
        lang = user['language']
        if first_entry:
            self.bot.send_message(message.chat.id, LANG_DICT[lang]['choose_notifications_msg'],
                                  reply_markup=keyboards.set_notifications_keyboard(lang, message.chat.id))
        else:
            if message.text == LANG_DICT[lang]['return_btn']:
                self.go_to_state(message, 'settings_state')

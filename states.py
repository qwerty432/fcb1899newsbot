import users_controller
import keyboards
import parse


class States(object):
    def __init__(self, bot):
        self.bot = bot
        self.states = {'start': self.start_state, 'next_match_state': self.next_match_state,
                       'time_state': self.time_state}

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
                self.go_to_state(message, 'next_match_state')
            elif message.text == 'Новости':
                self.bot.send_message(message.chat.id, 'Последние новости:',
                                      reply_markup=keyboards.set_news_buttons(message.chat.id))
            elif message.text == 'Время':
                self.go_to_state(message, 'time_state')
            else:
                self.bot.send_message(message.chat.id, 'Hello there!',
                                      reply_markup=keyboards.set_main_keyboard())

    def next_match_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, parse.parse_info(),
                                  reply_markup=keyboards.set_return_keyboard())
        else:
            self.go_to_state(message, 'start')

    def time_state(self, message, first_entry=False):
        if first_entry:
            self.bot.send_message(message.chat.id, parse.parse_time(),
                                  reply_markup=keyboards.set_return_keyboard())
        else:
            self.go_to_state(message, 'start')

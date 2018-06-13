import users_controller
import keyboards


class States(object):
    def __init__(self, bot):
        self.bot = bot
        self.states = {'start': self.start_state
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
            self.bot.send_message(message.chat.id, 'Again here')

from telebot import TeleBot
import config
from bot import bot
from states import States
import users_controller

state_handler = States(bot)

@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user = users_controller.get_user(message.chat.id)
        if user is None:
            users_controller.create_user(message)
        else:
            users_controller.update_state(message.chat.id, 'start')

        state_handler.handle_states(message, first_entry=True)
    except Exception as e:
        print('[ERROR]: {}'.format(e))


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        state_handler.handle_states(message)
    except Exception as e:
        print('[ERROR]: {}'.format(e))


if __name__ == '__main__':
    bot.polling(none_stop=True)

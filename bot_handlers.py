from telebot import TeleBot
import config
from bot import bot
from states import States
import users_controller
import parse

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


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        user = users_controller.get_user(call.message.chat.id)
        for i, url in enumerate(user['news_urls']):
            if call.data == "button{}".format(i):
                instant_view = parse.create_instant_view(url)
                if len(instant_view) == 2:
                    bot.send_message(call.message.chat.id, instant_view[0])
                    sleep(1)
                    bot.send_message(call.message.chat.id, instant_view[1])
                else:
                    bot.send_message(call.message.chat.id, instant_view)


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)

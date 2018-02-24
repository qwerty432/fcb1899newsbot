from flask import Flask, request
import telebot, json
from constants import token, secret
from datetime import datetime


# def write_json(data, filename='answer.json'):
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

global ten_urls


bot = telebot.TeleBot(token, threaded=False)
app = Flask(__name__)

bot.remove_webhook()
bot.set_webhook(url="https://dimakit.pythonanywhere.com/{}".format(secret))



#function for writing logs of every message
def write_logs(message, username, chat_id, time) :
    with open('logs.txt', 'a') as file :
        file.write('\n' + message + '\n' + username  + '\n' + str(chat_id) +\
                     '\n' + str(time) + '\n')


@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


#handler for '/start' command
@bot.message_handler(commands=['start'])
def start_command(message) :
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())
    print(message)
    bot.reply_to(message, "Welcome! Here you can find news about Barcelona :)")


#handler for '/help' command
@bot.message_handler(commands=['help'])
def help_command(message) :
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())
    bot.reply_to(message, "Памагити")


#handler for /next command
@bot.message_handler(commands=['next'])
def next_command(message) :
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())
    bot.send_message(message.chat.id, parse.parse_info())



#handler for '/time' command
@bot.message_handler(commands=['time'])
def time_command(message) :
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())
    bot.send_message(message.chat.id, "Time to next match: {}".format(parse.parse_time()))



#handler for '/news' command
@bot.message_handler(commands=['news'])
def news_command(message) :
    global ten_urls
    ten_urls = []
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())

    keyboard = telebot.types.InlineKeyboardMarkup()
    news = parse.parse_latest_news()
    titles = news[0]
    ten_urls.extend(news[1])
    callback_buttons = []
    for i in range(len(titles)) :
        callback_buttons.append(telebot.types.InlineKeyboardButton(text=titles[i], callback_data="test{}".format(i)))

    for button in callback_buttons :    
        keyboard.add(button)
    
    bot.send_message(message.chat.id, "Last news:", reply_markup=keyboard)




@bot.message_handler(content_types=["text"])
def any_msg(message):
    write_logs(message.text, message.from_user.username, message.chat.id, datetime.now())
    bot.send_message(message.chat.id, "You said: {}".format(message.text))



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global ten_urls
    if call.message:
        for i in range(len(ten_urls)) :
            if call.data == "test{}".format(i):
                instant_view = parse.create_instant_view(ten_urls[i])
                if(len(instant_view)) == 2 :
                    bot.send_message(call.message.chat.id, instant_view[0])
                    sleep(1)
                    bot.send_message(call.message.chat.id,  instant_view[1])
                else :
                    bot.send_message(call.message.chat.id, instant_view)         





if __name__ == '__main__':
    app.run()
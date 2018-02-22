from flask import Flask, request
import telebot, json
from constants import token, secret
from datetime import datetime


# def write_json(data, filename='answer.json'):
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)


bot = telebot.TeleBot(token, threaded=False)
app = Flask(__name__)

bot.remove_webhook()
bot.set_webhook(url="https://dimakit.pythonanywhere.com/{}".format(secret))



#function for writing logs of every message
def write_logs(message, chat_id, time) :
    with open('logs.txt', 'a') as file :
        file.write('\n' + message + '\n' + str(chat_id) + '\n' + str(time) + '\n')



@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


#handler for '/start' command
@bot.message_handler(commands=['start'])
def start_command(message) :
    write_logs(message.text, message.chat.id, datetime.now())
    print(message)
    bot.reply_to(message, "Welcome! Here you can find news about Barcelona :)")


#handler for '/help' command
@bot.message_handler(commands=['help'])
def help_command(message) :
    write_logs(message.text, message.chat.id, datetime.now())
    bot.reply_to(message, "Памагити")


#handler for '/time' command
@bot.message_handler(commands=['time'])
def time_command(message) :
    write_logs(message.text, message.chat.id, datetime.now())
    bot.reply_to(message, parse.parse_time())



#handler for '/news' command
@bot.message_handler(commands=['news'])
def news_command(message) :
    write_logs(message.text, message.chat.id, datetime.now())

    keyboard = telebot.types.InlineKeyboardMarkup()
    # news = parse.get_latest_news()
    # if len(news) == 2 :
    #     bot.reply_to(message, news[0])
    #     sleep(3)
    #     bot.reply_to(message, news[1])
    # else :
    #     bot.reply_to(message, news)
    news = parse.parse_latest_news()
    titles = news[0]
    callback_buttons = []
    for i in range(len(titles)) :
        callback_buttons.append(telebot.types.InlineKeyboardButton(text=titles[i], callback_data="test{}".format(i)))

    for button in callback_buttons :    
        keyboard.add(button)
    
    bot.send_message(message.chat.id, "Last news:", reply_markup=keyboard)



@bot.message_handler(content_types=["text"])
def any_msg(message):
    write_logs(message.text, message.chat.id, datetime.now())
    bot.send_message(message.chat.id, "You said: {}".format(message.text))




if __name__ == '__main__':
    app.run()
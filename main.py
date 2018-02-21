from flask import Flask, request
import telebot, json
from constants import token, secret


# def write_json(data, filename='answer.json'):
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)


bot = telebot.TeleBot(token, threaded=False)
app = Flask(__name__)

bot.remove_webhook()
bot.set_webhook(url="https://dimakit.pythonanywhere.com/{}".format(secret))



@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


#handler for '/start' command
@bot.message_handler(commands=['start'])
def start_command(message) :
    print(message)
    bot.reply_to(message, "Welcome! Here you can find news about Barcelona :)")


#handler for '/help' command
@bot.message_handler(commands=['help'])
def help_command(message) :
    bot.reply_to(message, "Памагити")


#handler for '/time' command
@bot.message_handler(commands=['time'])
def time_command(message) :
    bot.reply_to(message, parse.parse_time())



#handler for '/news' command
@bot.message_handler(commands=['news'])
def news_command(message) :
    news = parse.get_latest_news()
    if len(news) == 2 :
        bot.reply_to(message, news[0])
        sleep(3)
        bot.reply_to(message, news[1])
    else :
        bot.reply_to(message, news)



@bot.message_handler(content_types=['text'])
def text_response(message) :
    bot.reply_to(message, "you said '{}'".format(message.text))




if __name__ == '__main__':
    app.run()
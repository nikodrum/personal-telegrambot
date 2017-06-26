from flask import Flask, request
import telebot
import time
from datetime import datetime
from models import Frame, Speech, Gif
from config import *
from loggers import logger
import os

# CONFIG
TOKEN = os.environ['BOT_TOKEN']
HOST = WEBHOOK_LISTEN
PORT = WEBHOOK_PORT
CERT = WEBHOOK_SSL_CERT
CERT_KEY = WEBHOOK_SSL_PRIV

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
del app.logger.handlers[:]
for hdlr in logger.handlers:
    app.logger.addHandler(hdlr)

context = (CERT, CERT_KEY)


@app.route('/' + TOKEN, methods=['POST'])
def process_updates():
    length = int(request.headers['content-length'])
    json_string = request.data.decode("utf-8")[:length]
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK'


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    u_id = message.chat.id
    app.logger.info("Processing request from {}.".format(u_id))

    speech = Speech()
    speech_request = speech.recognize(message.text)
    app.logger.info("Preparing {} for {}.".format(speech_request, u_id))

    today_str = str(datetime.now().date())
    if speech_request == "frame":
        frame = Frame(file_path="./data/temp/frame.jpg")
        frame.download_video("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
        frame_path = frame.get()

        app.logger.info("File size is : %s" % os.stat(frame_path).st_size)
        bot.send_photo(u_id, open(frame_path, 'rb'))
        logger.info("Done with {}.".format(u_id))

    if speech_request == "gif":
        gif_path = "./data/{}/{}.gif".format(speech_request, today_str)
        if os.path.exists(gif_path):
            bot.send_photo(u_id, open('./data/gif/%s.gif' % today_str, 'rb'))
        else:
            if not os.path.exists("./data/gif/{}.gif".format(today_str)):
                gif = Gif(today_str)
                gif.create()
            try:
                bot.send_document(u_id, open('./data/gif/%s.gif' % today_str, 'rb'))
            finally:
                bot.send_message(u_id, "Не получается сохранить гифку 😭")


def set_webhook():
    bot.set_webhook(url='https://%s:%s/%s' % (HOST, PORT, TOKEN),
                    certificate=open(CERT, 'rb'))


if __name__ == '__main__':
    set_webhook()

    time.sleep(5)
    app.run(host='0.0.0.0',
            port=PORT,
            ssl_context=context,
            debug=True)

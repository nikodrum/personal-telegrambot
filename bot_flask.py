from flask import Flask, request
from config import *
import telebot
import time

# CONFIG
TOKEN = os.environ['BOT_TOKEN']
HOST = WEBHOOK_LISTEN
PORT = WEBHOOK_PORT
CERT = WEBHOOK_SSL_CERT
CERT_KEY = WEBHOOK_SSL_PRIV

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
context = (CERT, CERT_KEY)


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    length = int(request.headers['content-length'])
    json_string = request.body.read(length).decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK'


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(chat_id=message.chat.id, text='Hello, there')


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

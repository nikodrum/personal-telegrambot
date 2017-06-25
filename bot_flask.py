from flask import Flask, request
from config import *
import telegram

# CONFIG
TOKEN = os.environ['BOT_TOKEN']
HOST = WEBHOOK_LISTEN
PORT = WEBHOOK_PORT
CERT = WEBHOOK_SSL_CERT
CERT_KEY = WEBHOOK_SSL_PRIV

bot = telegram.Bot(TOKEN)
app = Flask(__name__)
context = (CERT, CERT_KEY)


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telegram.update.Update.de_json(request.get_json(force=True))
    bot.sendMessage(chat_id=update.message.chat_id, text='Hello, there')

    return 'OK'


def set_webhook():
    bot.set_webhook(url='https://%s:%s/%s' % (HOST, PORT, TOKEN),
                    certificate=open(CERT, 'rb'))


if __name__ == '__main__':
    set_webhook()

    app.run(host='0.0.0.0',
            port=PORT,
            ssl_context=context,
            debug=True)

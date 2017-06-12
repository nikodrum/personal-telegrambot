import cherrypy
import telebot
import time
import logging
from models import Frame
from config import *

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

logger = logging.getLogger(__name__)


class BotServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "New message received."
        else:
            raise cherrypy.HTTPError(403)

    @staticmethod
    @bot.message_handler(content_types=["text"])
    def repeat_all_messages(message):
        start_time = 0
        cherrypy.log("Processing request from {}".format(message.chat.id))
        if int(time.time()) - start_time > 15 * 60:
            frame = Frame()
            frame.download_video("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
            frame.get()
        cherrypy.log("File size is :" + str(os.stat('frame10.jpg').st_size))
        bot.send_photo(message.chat.id, open('frame10.jpg', 'rb'))


cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV,
    'log.screen': False,
    'log.error_file': "./logs/error.log",
    'log.access_file': "./logs/access_file.log"
})


cherrypy.quickstart(BotServer(), WEBHOOK_URL_PATH, {'/': {}})

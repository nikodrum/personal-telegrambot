import cherrypy
import telebot
import time
from datetime import datetime
from models import Frame, Recognize, Gif
from config import *

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))


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
        u_id = message.chat.id
        cherrypy.log("Processing request from {}.".format(u_id))

        request = Recognize(message)
        cherrypy.log("Preparing {} for {}.".format(request, u_id))

        today_str = str(datetime.now().date())
        if request is "frame":
            frame = Frame(file_path="./data/temp/frame.jpg")
            frame.download_video("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
            frame_path = frame.get()

            cherrypy.log("File size is : " % os.stat(frame_path).st_size)
            bot.send_photo(u_id, open(frame_path, 'rb'))

        if request is "gif":
            gif_path = "./data/{}/{}.gif".format(request, today_str)
            if os.path.exists(gif_path):
                bot.send_photo(u_id, open('./data/gif/%s.gif' % today_str, 'rb'))
            else:
                gif = Gif(today_str)
                if gif.create():
                    bot.send_photo(u_id, open('./data/gif/%s.gif' % today_str, 'rb'))
                else:
                    bot.send_message(u_id, "Не получается сохранить гифку 😭")

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV,
    'logs.screen': False,
    'logs.error_file': "./logs/error.logs",
    'logs.access_file': "./logs/access_file.logs"
})


cherrypy.quickstart(BotServer(), WEBHOOK_URL_PATH, {'/': {}})

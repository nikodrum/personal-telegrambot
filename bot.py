import telebot
import cherrypy
import os
import cv2
from logger import logger
import requests
import time

WEBHOOK_HOST = 'provide here server ip'
WEBHOOK_PORT = 80
WEBHOOK_LISTEN = 'provide here server ip'

WEBHOOK_SSL_CERT = './webhook/webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook/webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (os.environ['BOT_TOKEN'])

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
    def download_file(url):
        r = requests.get(url, stream=True)
        with open("video.mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    @staticmethod
    def get_frame():
        cap = cv2.VideoCapture('./video.mp4')
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count == 10:
                cv2.imwrite("frame%d.jpg" % count, frame)
                break
            count += 1
        cap.release()

    @bot.message_handler(content_types=["text"])
    def repeat_all_messages(self, message):
        start_time = 0
        if int(time.time()) - start_time > 15 * 60:
            self.download_file("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
            self.get_frame()
        logger.info("File size is :" + str(os.stat('frame10.jpg').st_size))
        bot.send_photo(message.chat.id, open('frame10.jpg', 'rb'))


cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})


cherrypy.quickstart(BotServer(), WEBHOOK_URL_PATH, {'/': {}})

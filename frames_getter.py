from database import SQLighter
from datetime import datetime
from models import Gif, Frame
from loggers import logger
from pytz import timezone
import os
import json
import time
import telebot
import requests

TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(TOKEN)
db_worker = SQLighter(database="bot.db")


def get_sunset_sunrise():

    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q=Kiev&APPID={}"
            .format(os.environ['WEATHER_KEY'])
    )
    weather_data = json.loads(resp.content.decode())

    sunrise_utc = datetime.fromtimestamp(weather_data['sys']['sunrise'])\
        .replace(tzinfo=timezone('UTC'))

    sunset_utc = datetime.fromtimestamp(weather_data['sys']['sunset'])\
        .replace(tzinfo=timezone('UTC'))

    return sunrise_utc, sunset_utc


def set_constants():
    sun_info = get_sunset_sunrise()

    global DAILY_CONST
    DAILY_CONST = {
        "CURRENT_DAY": str(datetime.now().date()),
        "GIF_NEEDED": True,
        "SUN_RISE": sun_info[0],
        "SUN_SET": sun_info[1]
    }
    folder_path = './data/frames/%s' % datetime.today().date()
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    logger.info("Constants set to {}".format(str(DAILY_CONST)))


def mail_gif(name):

    users_list = db_worker.get_users_with_mailing({})

    file_id = None
    for user in users_list:
        if not file_id:
            gif_data = open(name, 'rb')
            msg = bot.send_document(chat_id=user[0], data=gif_data)
            db_worker.post_file(file_id=msg.document.file_id, file_type="gif")
            file_id = msg.document.file_id
        else:
            bot.send_document(chat_id=user[0], data=file_id)
    return len(users_list)


def run_conditions():
    now_date = datetime.utcnow()
    now_date = now_date.replace(tzinfo=timezone('UTC'))
    logger.info("Now is {}".format(now_date))

    if DAILY_CONST['SUN_RISE'] < now_date < DAILY_CONST["SUN_SET"]:

        logger.info("Getting new frame.")

        try:
            frame = Frame(file_path="./data/frames/{}/{}.jpg".format(
                DAILY_CONST["CURRENT_DAY"],
                int(time.time())
            ))
            frame.download_video("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
            file_path = frame.get()
            if file_path.split("/")[-1] in os.listdir('./data/frames/%s' % DAILY_CONST["CURRENT_DAY"]):
                logger.info("Getting succeed. Saved at '%s'" % file_path)
            else:
                logger.warning("Getting failed.")
            del frame
        except Exception as e:
            logger.warning("Failed downloading frame with error : '%s'" % e)

    if DAILY_CONST["GIF_NEEDED"] and datetime.now().hour > 16:

        logger.info("Started making GIF.")

        gif = Gif(DAILY_CONST["CURRENT_DAY"])
        frames_list = gif.load_all_images(DAILY_CONST["CURRENT_DAY"])
        logger.info("Got %d frames. " % len(frames_list))
        gif_name = gif.build(frames=frames_list)
        if gif_name:
            DAILY_CONST["GIF_NEEDED"] = False
            logger.info("Making succeed. Saved at %s" % gif_name)
            number = mail_gif(gif_name)
            logger.info("Mailed to %s users." % number)
            del gif

    if DAILY_CONST["CURRENT_DAY"] != str(datetime.now().date()):

        try:
            logger.info("Updating constants.")
            set_constants()
        except Exception as e:
            logger.info("Failed updating constants with error : '%s'" % e)


if __name__ == '__main__':

    logger.info("Script initialized.")
    set_constants()

    while True:
        run_conditions()
        time.sleep(60 * 30)


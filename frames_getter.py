from datetime import datetime
from models import Gif, Frame
import os
import logging
import time

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                    level='DEBUG',
                    filename=u'./logs/frames_getter.log')
logger_getter = logging.getLogger(__name__)


def set_constants():
    global INIT_HOURS
    INIT_HOURS = [h - 3 for h in range(9, 19)]
    global CURRENT_DAY
    CURRENT_DAY = datetime.now().date()
    global GIF_NEEDED
    GIF_NEEDED = True


if __name__ == '__main__':

    logger_getter.info("Script initialized.")
    set_constants()

    while True:

        if datetime.now().hour in INIT_HOURS:

            logger_getter.info("Getting new frame.")

            try:
                INIT_HOURS.remove(datetime.now().hour)
                frame = Frame(file_path="./data/frame/{}/{}.jpg".format(
                    str(CURRENT_DAY),
                    int(time.time())
                ))
                file_path = frame.get()
                if file_path in os.listdir('./data/frames/%s' % CURRENT_DAY):
                    logger_getter.info("Getting succeed.")
                else:
                    logger_getter.info("Getting failed.")
            except Exception as e:
                logger_getter.info("Failed downloading frame with error : '%s'" % e)

        if GIF_NEEDED and datetime.now().hour > 16:

            logger_getter.info("Started making GIF.")

            gif = Gif(str(CURRENT_DAY))
            frames_list = gif.load_all_images(str(CURRENT_DAY))
            logger_getter.info("Got %d frames. " % len(frames_list))
            if gif.build(frames=frames_list):
                GIF_NEEDED = False
                logger_getter.info("Making succeed.")

        if CURRENT_DAY != datetime.now().date():

            try:
                logger_getter.info("Updating constants.")
                set_constants()
                os.makedirs('./data/frames/%s' % datetime.today().date())
            except Exception as e:
                logger_getter.info("Failed updating constants with error : '%s'" % e)
        time.sleep(60 * 60)

from datetime import datetime
from models import Gif, Frame
import os
from loggers import logger
import time


def set_constants():
    global DAILY_CONST
    DAILY_CONST = {
        "INIT_HOURS": [h - 3 for h in range(9, 19)],
        "CURRENT_DAY": str(datetime.now().date()),
        "GIF_NEEDED": True
    }
    folder_path = './data/frames/%s' % datetime.today().date()
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    logger.info("Constants set to {}".format(str(DAILY_CONST)))

if __name__ == '__main__':

    logger.info("Script initialized.")
    set_constants()

    while True:

        if True:#datetime.now().hour in DAILY_CONST["INIT_HOURS"]:

            logger.info("Getting new frame.")

            try:
                frame = Frame(file_path="./data/frame/{}/{}.jpg".format(
                    DAILY_CONST["CURRENT_DAY"],
                    int(time.time())
                ))
                file_path = frame.get()
                if file_path in os.listdir('./data/frames/%s' % DAILY_CONST["CURRENT_DAY"]):
                    logger.info("Getting succeed. Saved at '%s'" % file_path)
                    #DAILY_CONST["INIT_HOURS"].remove(datetime.now().hour)
                else:
                    logger.warning("Getting failed.")
            except Exception as e:
                logger.warning("Failed downloading frame with error : '%s'" % e)

        if DAILY_CONST["GIF_NEEDED"] and datetime.now().hour > 16:

            logger.info("Started making GIF.")

            gif = Gif(DAILY_CONST["CURRENT_DAY"])
            frames_list = gif.load_all_images(DAILY_CONST["CURRENT_DAY"])
            logger.info("Got %d frames. " % len(frames_list))
            gif_name = gif.build(frames=frames_list)
            if gif_name:
                GIF_NEEDED = False
                logger.info("Making succeed. Saved at %s" % gif_name)

        if DAILY_CONST["CURRENT_DAY"] != str(datetime.now().date()):

            try:
                logger.info("Updating constants.")
                set_constants()
            except Exception as e:
                logger.info("Failed updating constants with error : '%s'" % e)
        time.sleep(60 * 60)

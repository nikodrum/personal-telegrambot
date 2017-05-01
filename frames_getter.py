from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import requests
import cv2
import logging
import time

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                    level='DEBUG',
                    filename=u'frames_getter.log')
logger = logging.getLogger(__name__)


def set_constants():
    global INIT_HOURS
    INIT_HOURS = [h - 3 for h in range(9, 19)]
    global CURRENT_DAY
    CURRENT_DAY = datetime.now().date()
    global GIF_NEEDED
    GIF_NEEDED = True


def download_file(url):
    r = requests.get(url, stream=True)
    with open("./data/temp/video.mp4", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return True


def get_frame(file):
    cap = cv2.VideoCapture('./data/temp/video.mp4')
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if count == 10:
            cv2.imwrite('./data/frames/{}/{}'.format(datetime.today().date(), file), frame)
            break
        count += 1
    cap.release()


def load_all_images(frames_dir):
    frames = []
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    for frame_name in os.listdir(frames_dir):
        img = cv2.imread(os.path.join(frames_dir, frame_name), cv2.IMREAD_COLOR)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frames.append(img)

    return frames


def build_gif(frames, title=''):

    logger.info("Started making new gif...")
    fig = plt.figure(figsize=[12.8, 7.2], frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ims = [(plt.imshow(x), ax.set_title(title)) for x in frames]
    im_ani = animation.ArtistAnimation(fig, ims, interval=100, repeat_delay=0, blit=True)
    logger.info("GIF successfully created.")
    im_ani.save('./data/gif/%s.gif' % round(time.time(), 0), writer='imagemagick', dpi=60)
    logger.info("GIF successfully saved.")

    return plt.show()


if __name__ == '__main__':

    logger.info("Script initialized.")
    set_constants()

    while True:

        if datetime.now().hour in INIT_HOURS:

            logger.info("Getting new frame.")

            INIT_HOURS.remove(datetime.now().hour)
            download_file("http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4")
            file_name = str(round(time.time(), 0)) + '.jpg'
            get_frame(file_name)

            if file_name in os.listdir('./data/frames/%s' % datetime.today().date()):
                logger.info("Getting succeed.")
            else:
                logger.info("Getting failed.")

        if GIF_NEEDED and datetime.now().hour > 16:

            logger.info("Started making GIF.")

            frames_list = load_all_images("./data/frames/%s" % datetime.today().date())
            logger.info("Got %d frames. " % len(frames_list))
            build_gif(frames=frames_list)

            GIF_NEEDED = False

            logger.info("Making succeed.")

        if CURRENT_DAY != datetime.now().date():

            logger.info("Updating constants.")
            set_constants()
            os.makedirs('./data/frames/%s' % datetime.today().date())

        time.sleep(60 * 60)
import cherrypy
import cv2
import matplotlib
import os
import re
import requests
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime


class Frame(object):
    def __init__(self, file_path, url="http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4"):
        self.url = url
        self.file_path = file_path

    @staticmethod
    def download_video(url):
        r = requests.get(url, stream=True)
        with open("./data/temp/video.mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    def get(self):

        cap = cv2.VideoCapture('./data/temp/video.mp4')
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count == 10:
                cv2.imwrite(self.file_path, frame)
                break
            count += 1
        cap.release()
        return self.file_path


class Gif(object):

    def __init__(self, today_day: str):
        self.today_day = today_day
        self.filename = "{}.{}".format(today_day, "gif")
        self.frames_dir = "./data/frames/"

    def load_all_images(self, date: str):

        frames = []
        frames_date_dir = self.frames_dir + date
        if not os.path.exists(frames_date_dir):
            os.makedirs(frames_date_dir)

        frame_names_list = os.listdir(frames_date_dir)
        cherrypy.log("Found {} frames files at {}.".format(len(frame_names_list),
                                                           frames_date_dir))

        for frame_name in frame_names_list:
            img = cv2.imread(os.path.join(frames_date_dir, frame_name), cv2.IMREAD_COLOR)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                frames.append(img)

        return frames

    def build(self, frames, title=''):

        cherrypy.log("Started making new gif...")
        fig = plt.figure(figsize=[12.8, 7.2], frameon=False)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        ims = [(plt.imshow(x), ax.set_title(title)) for x in frames]
        im_ani = animation.ArtistAnimation(fig, ims, interval=100, repeat_delay=0, blit=True)
        cherrypy.log("GIF successfully created.")
        try:
            file_path = './data/gif/%s' % self.filename
            im_ani.save(file_path, writer='imagemagick', dpi=60)
            cherrypy.log("GIF successfully saved. File size is {}kb.".format(
                str(round(os.stat(file_path).st_size/1024, 0))))
        except Exception:
            cherrypy.log.error("Saving GIF failed with error ", traceback=True)
            return False
        plt.close()
        return True

    def create(self):

        frames = self.load_all_images(self.today_day)
        if len(frames) != 0:
            return self.build(frames=frames)

        return False


class Recognize(object):

    def __init__(self, message):
        self.message = message

    def recognize(self):
        if re.findall(r"гиф", self.message):
            return "gif"
        else:
            return "frame"

    def __call__(self, *args, **kwargs):
        self.recognize()

import requests
import cv2


class Frame(object):

    def __init__(self, url="http://vs8.videoprobki.com.ua/tvukrbud/cam17.mp4"):
        self.url = url

    @staticmethod
    def download_video(url):
        r = requests.get(url, stream=True)
        with open("video.mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    @staticmethod
    def get():
        cap = cv2.VideoCapture('./video.mp4')
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if count == 10:
                cv2.imwrite("frame%d.jpg" % count, frame)
                break
            count += 1
        cap.release()
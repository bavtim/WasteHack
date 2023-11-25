import json
import tkinter
import uuid
from tkinter import ttk
from tkinter import filedialog as fd
import os
import cv2
import PIL.Image
import PIL.ImageTk
import requests
from tkinter.messagebox import showinfo
import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

url = 'http://127.0.0.1:8000/'


def time_crop_video(path_video):
    '''
    Функция принимает на вход видео и обрезает его по времени приезда самосвала
    '''
    time_start_in_second = 110  # 1 min 50 sec
    time_end_in_second = 150  # 2 min 30 sec
    uid = str(uuid.uuid4())
    name_crop_video = uid + ".mp4"

    ffmpeg_extract_subclip(path_video,
                           time_start_in_second,
                           time_end_in_second,
                           targetname=name_crop_video)

    return name_crop_video

def format_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    return "{:02}:{:02}".format(int(minutes), int(seconds))
class App:
    def update_ts(self,current,full):
        sec_cur=current*self.delay
        sec_full = full* self.delay
        self.timecode.set(f"{format_seconds(sec_cur//1000)}/{format_seconds(sec_full//1000)}")
    def updatestatus(self, dict):
        temp_s = "Анализ результатов:\n"
        t = 0
        ddict = {k: v for k, v in dict.items() if k != 'bb_vid'}
        dddict = {}
        for i in ddict:
            a = (list(ddict[i].keys())[0])
            dddict.update({i: int(a)})
        dddict_rev = sorted(dddict, key=lambda k: int(dddict[k]), reverse=True)
        rez = {'beton': "Бетон", 'brezent': "Брезент", "dirt": "Грунт", "empty": "Пустой кузов", "wood": "Дерево"}
        temp_s = f"Главный класс:\n {rez[dddict_rev[0]]} - уверенность {list(ddict[dddict_rev[0]].values())[0]}\n"
        if list(ddict[dddict_rev[1]].values())[0] != 0 and \
                list(ddict[dddict_rev[1]].values())[0] / list(ddict[dddict_rev[0]].values())[0] > 0.5:
            temp_s += f"Второй класс:\n  {rez[dddict_rev[1]]} - уверенность {list(ddict[dddict_rev[1]].values())[0]}\n"
        self.status.set(temp_s)

    def __init__(self, window, video_source1, video_source2, statusdict):
        self.delay = 83
        self.status = tkinter.StringVar()
        self.timecode = tkinter.StringVar()
        self.timecode.set("00:00/00:00")
        self.status.set("Статистика: ")
        self.statusdict = statusdict
        self.updatestatus(self.statusdict)
        self.window = window
        self.window.geometry("840x400")
        self.window.title("")
        self.video_source1 = video_source1
        self.video_source2 = video_source2
        self.photo1 = ""
        self.photo2 = ""

        # open video source
        self.vid1 = MyVideoCapture(self.video_source1, self.video_source2)

        # Create a canvas that can fit the above video source size
        self.info_label = ttk.Label(window, text="Входной поток данных")
        self.info_label.config(font=("Courier", 10))
        self.info_label.grid(row=0, column=0, padx=5, pady=10)
        self.info_label = ttk.Label(window, text="Выходной поток данных")
        self.info_label.config(font=("Courier", 10))
        self.info_label.grid(row=0, column=1, padx=5, pady=10)
        self.canvas1 = tkinter.Canvas(window, width=300, height=300)
        self.canvas2 = tkinter.Canvas(window, width=300, height=300)
        self.canvas1.grid(row=1, column=0, padx=5, pady=10)
        self.canvas2.grid(row=1, column=1, padx=5, pady=10)

        # Add a label to the right of the videos
        self.info_label = ttk.Label(window, textvariable=self.status)
        self.info_label.config(font=("Courier", 10))
        self.info_label.grid(row=1, column=2, padx=5, pady=10, sticky='nw')
        self.info_label = ttk.Label(window,textvariable=self.timecode)
        self.info_label.config(font=("Courier", 10))
        self.info_label.grid(row=2, column=2, padx=5, pady=10, sticky="w")
        # Add a scale/slider for controlling the video position
        self.scale = ttk.Scale(window, from_=0, to=100, orient="horizontal")
        self.scale.bind("<B1-Motion>", lambda event: self.update_video_position(self.scale.get()))
        # self.scale.bind("<ButtonRelease-1>", self.frame_free())
        self.scale.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky='ew')

        # After it is called once, the update method will be automatically called every delay milliseconds

        self.update()

        self.window.mainloop()

    def update(self):

        start = time.time()
        # Get a frame from the video source
        # if (not frame_blocker):
        ret1, frame1, ret2, frame2 = self.vid1.get_frame()

        if ret1 and ret2:
            # self.canvas1.delete(self.photo1)
            # self.canvas2.delete(self.photo2)
            self.photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
            self.photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame2))
            self.canvas1.create_image(0, 0, image=self.photo1, anchor=tkinter.NW)
            self.canvas2.create_image(0, 0, image=self.photo2, anchor=tkinter.NW)

            # Update the scale/slider position based on the video position
            total_frames = self.vid1.get_total_frames()
            self.update_ts(self.vid1.get_current_frame(),self.vid1.get_total_frames())
            if total_frames > 0:
                if not frame_blocker:
                    position = (self.vid1.get_current_frame() / total_frames) * 100
                    self.scale.set(position)
            print(total_frames,self.vid1.get_current_frame() )

        end = time.time() - start
        self.frame_free()
        # print(end)
        self.window.after(self.delay, self.update)

    def frame_free(self):

        # Update the video position based on the scale/slider position
        global frame_blocker
        frame_blocker = False

    def frame_lock(self):
        # Update the video position based on the scale/slider position
        global frame_blocker
        frame_blocker = True

    def update_video_position(self, position):
        self.frame_lock()
        # Update the video position based on the scale/slider position

        total_frames = self.vid1.get_total_frames()
        target_frame = int((float(position) / 100) * total_frames)
        # print(target_frame)
        self.vid1.set_current_frame(target_frame)


frame_blocker = False


class MyVideoCapture:
    global frame_blocker

    def __init__(self, video_source1, video_source2):
        # Open the video source

        self.vid1 = cv2.VideoCapture(time_crop_video(video_source1))
        self.vid2 = cv2.VideoCapture(video_source2)

        if not self.vid1.isOpened():
            raise ValueError("Unable to open video source", video_source1)
        if not self.vid2.isOpened():
            raise ValueError("Unable to open video source", video_source2)
        self.current_frame = 0

    def get_frame(self):
        ret1 = ""
        ret2 = ""
        if self.vid1.isOpened() and self.vid2.isOpened():
            ret1, frame1 = self.vid1.read()
            ret2, frame2 = self.vid2.read()

            if ret1 and ret2:
                frame1 = cv2.resize(frame1, (300, 300))
                frame2 = cv2.resize(frame2, (300, 300))
                self.current_frame += 1
                return ret1, cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB), ret2, cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            else:

                return ret1, None, ret2, None
        else:

            return ret1, None, ret2, None

    def get_total_frames(self):
        return int(self.vid2.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_current_frame(self):
        return self.current_frame

    def set_current_frame(self, frame_number):
        # print("afwfwfawff")
        self.vid1.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.vid2.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number

    def __del__(self):
        if self.vid1.isOpened():
            self.vid1.release()
        if self.vid2.isOpened():
            self.vid2.release()


def callback():
    initial.destroy()


def select_file():
    filetypes = (
        ('video mp4', '*.mp4'),
    )

    filename = fd.askopenfilename(
        title='Выбор файла',
        initialdir='/',
        filetypes=filetypes)
    if (len(filename) > 10):
        showinfo(
            title='Информация',
            message="Вы выбрали видео, оно будет отправлено на сервер и обработано."
        )
        files = {'file': (os.path.basename(filename), open(filename, 'rb'))}
        response = requests.post(url + "file/upload-file", files=files)
        global v1, v2, stat
        v1 = filename
        # v2 = filename
        # stat = {"f": 11}
        j=json.loads(response.text)
        stat=j
        r = requests.get(url + f"file/{j['bb_vid']}", allow_redirects=True)
        id = uuid.uuid4()
        file_location = f"files/{id}.mp4"
        with open(file_location, "wb+") as file_object:
            file_object.write(r.content)
        v2 = file_location
        scoreinfo=response.text
        scoreinfo = ""
        # print(scoreinfo)

        callback()


initial = tkinter.Tk()
initial.title("Выбор файла")
initial.geometry("250x100")
open_button = ttk.Button(
    initial,
    text='Выбор файла',
    command=select_file
)
open_button.pack(expand=True)

initial.mainloop()
# Create a window and pass it to the Application object
App(tkinter.Tk(), v1, v2, stat)

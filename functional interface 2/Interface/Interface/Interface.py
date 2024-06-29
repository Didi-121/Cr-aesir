import tkinter as tk
import threading
from camera import Camera
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
from Control_Service import Client

video_capture_1 = cv2.VideoCapture(1)
video_capture_2 = cv2.VideoCapture(2)
video_capture_3 = cv2.VideoCapture(3)
video_capture_4 = cv2.VideoCapture(4)

HOST = "169.254.111.111"
PORT = 5555
JSONPATH = r'B:\functional interface (ESTA ES)\Interface\Interface\Keys.json'
username = "aesir"

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.thread = None
        self.wm_title("Aesir interface")
        self.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("1920x1080")

        self.mainFrame = tk.Frame(self, background="gray")
        self.mainFrame.pack(fill="both",expand=True)

        self.create_widgets()
        self.cam()

        self.client = Client(HOST, PORT, username, JSONPATH, self.feed.change)


    def create_widgets(self):

        self.bg = Image.open("image/background.jpeg")
        self.bg = self.bg.resize((1536, 864))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.background = tk.Label(self.mainFrame, image=self.bg, borderwidth=0)

        self.background.place(x=0, y=0)

        self.feed = Camera(self.mainFrame, 1100, 700)

        self.connection_button = tk.Button(self, text="Connection Button", fg= "gold", bg = "black", command= self.server )
        self.connection_button.place (x=40, y=40, width=100, height=30)

    def onClose(self):
        self.quit()

    def server(self):
        self.server_thread = threading.Thread(target=self.client.main)
        self.server_thread.start()


    def cam(self):
        def capture_video():
            camara = cv2.VideoCapture(1)
            camara2 = cv2.VideoCapture(2)
            camara3 = cv2.VideoCapture(3)
            camara4 = cv2.VideoCapture(4)

            while True:
                ret1, framea = camara.read()
                ret2, frameb = camara2.read()
                ret3, framec = camara3.read()
                ret4, framed = camara4.read()

                if (ret1):
                    height, width = framea.shape[:2]

                    left1_frame = framea[:, :width // 2]
                    right_frame = framea[:, width // 2:]

                    overlay_frame = left1_frame.copy()
                    start_width = int(0.45 * width)
                    end_width = int(0.55 * width)
                    overlay_frame[:, start_width:end_width] = right_frame[:, start_width:end_width]
                    overlay2_frame = cv2.resize(overlay_frame, (640, 480))
                    cv2.imshow('Cam 1', overlay2_frame)

                if (ret2):
                    frameb_resized = cv2.resize(frameb, (640, 480))
                    cv2.imshow('Cam 2', frameb_resized)

                if (ret3):
                    framec_resized = cv2.resize(framec, (640, 480))
                    framec2_resized = cv2.flip(framec_resized, 0)
                    cv2.imshow('Cam 3', framec2_resized)

                if (ret4):
                    framed_resized = cv2.resize(framed, (640, 480))
                    cv2.imshow('Cam 4', framed_resized)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        self.thread = threading.Thread(target=capture_video)
        self.thread.start()

video_capture_1.release()
video_capture_2.release()
video_capture_3.release()
video_capture_4.release()
cv2.destroyAllWindows()

app = Application()

app.mainloop()
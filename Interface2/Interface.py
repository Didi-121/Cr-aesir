import tkinter as tk
import threading
from camera import Camera
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
from Control_Service import Client

#Camera configuration
video_capture_1 = cv2.VideoCapture(1)
video_capture_2 = cv2.VideoCapture(2)
video_capture_3 = cv2.VideoCapture(3)
video_capture_4 = cv2.VideoCapture(4)

#Server configuration
HOST = "169.254.111.111"
PORT = 5555
JSONPATH = 'Keys.json'
username = "aesir"

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.thread = None
        self.wm_title("Aesir interface")
        self.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("1920x1080")

        #Create the main frame with a gray background
        self.mainFrame = tk.Frame(self, background="gray")
        self.mainFrame.pack(fill="both",expand=True)

        #Set up widgets
        self.create_widgets()
        self.cam()

        #Initialize the client
        self.client = Client(HOST, PORT, username, self.feed.change)


    def create_widgets(self):

        #Load the background image
        self.bg = Image.open("image/background.jpeg")
        self.bg = self.bg.resize((1536, 864))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.background = tk.Label(self.mainFrame, image=self.bg, borderwidth=0)

        self.background.place(x=0, y=0)

        #Configure the camera feed
        self.feed = Camera(self.mainFrame, 1100, 700)

        #Server connection button
        self.connection_button = tk.Button(self, text="Connection Button", fg= "gold", bg = "black", command= self.server )
        self.connection_button.place (x=40, y=40, width=100, height=30)

    def onClose(self):
        self.quit()

    def server(self):
        #Start the client thread
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

                #Process camera frames
                if (ret1):

                    framea_resized = cv2.resize(framea, (640, 480))
                    framea2_resized = cv2.flip(framea_resized, 0)
                    cv2.imshow('Cam 1', framea2_resized)


                if (ret2):

                    height, width, _ = frameb.shape
                    half_width = width // 2
                    left_half = frameb[:, :half_width]
                    right_half = frameb[:, half_width:]

                    # Muestra cada mitad en una ventana diferente
                    cv2.imshow('Mitad izquierda', left_half)
                    cv2.imshow('Mitad derecha', right_half)

                if (ret3):

                    framec_resized = cv2.resize(framec, (640, 480))
                    cv2.imshow('Cam 4', framec_resized)

                if (ret4):
                    framed_resized = cv2.resize(framed, (640, 480))
                    cv2.imshow('Cam 4', framed_resized)


                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        #Start the video capture thread
        self.thread = threading.Thread(target=capture_video)
        self.thread.start()

#Release cameras and close windows
video_capture_1.release()
video_capture_2.release()
video_capture_3.release()
video_capture_4.release()
cv2.destroyAllWindows()

#Initialize the application
app = Application()
app.mainloop()

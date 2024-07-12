import tkinter as tk
import threading
from camera import Camera
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
from Control_Service import Client
import time

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

        self.second_window = VentanaSecundaria(self)

        #Create the main frame with a gray background
        self.mainFrame = tk.Frame(self, background="gray")
        self.mainFrame.pack(fill="both", expand=True)

        #Set up widgets
        self.create_widgets()

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
        self.connection_button = tk.Button(self, text="Connection Button", fg="gold", bg="black", command=self.server)
        self.connection_button.place(x=40, y=40, width=100, height=30)

    def onClose(self):
        self.quit()

    def server(self):
        #Start the client thread
        self.server_thread = threading.Thread(target=self.client.main)
        self.server_thread.start()


class VentanaSecundaria(tk.Toplevel):
    def __init__(self, parent):
        self.cam_on = None
        self.indexOfCamera2 = None

        self.camara0 = None
        self.camara1 = None
        self.camara2 = None
        self.camara3 = None
        self.cam0_State = None
        self.cam1_State = None
        self.cam2_State = None
        self.cam3_State = None

        self.lis_cam_states = [self.cam0_State, self.cam1_State, self.cam2_State, self.cam3_State]
        self.listcams = [self.camara0, self.camara1, self.camara2 ,self.camara3 ]

        super().__init__(parent)
        self.title("Ventana Secundaria")
        self.configure(bg="gray")
        self.geometry("1920x1080")

        self.Frame = tk.Frame(self, background="gray")
        self.Frame.pack(fill="both", expand=True)

        self.widgets_child()

        self.holder = Image.open("image/pepe3.jpeg")
        self.holder = self.holder.resize((1100, 700))
        self.holder = ImageTk.PhotoImage(self.holder)

        self.image = self.holder

        self.feed2 = tk.Label(master=self.Frame, image=self.holder, borderwidth=0)
        self.feed2.pack(padx=20, side="right")

        self.Cam0 = tk.Button(self, text="Cam 0", fg="gold", bg="white", command=lambda: self.change(0))
        self.Cam0.place(x=20, y=150, width=100, height=30)

        self.Cam1 = tk.Button(self, text="Cam 1", fg="gold", bg="white", command=lambda: self.change(1))
        self.Cam1.place(x=20, y=200, width=100, height=30)

        self.Cam2 = tk.Button(self, text="Cam 2", fg="gold", bg="white", command=lambda: self.change(2))
        self.Cam2.place(x=20, y=250, width=100, height=30)

        self.Cam3 = tk.Button(self, text="Cam 3", fg="gold", bg="white", command=lambda: self.change(3))
        self.Cam3.place(x=20, y=300, width=100, height=30)

        self.cambutonlist = [self.Cam0, self.Cam1, self.Cam2, self.Cam3]

        self.camera2chidatread = threading.Thread(target= self.camera_2_pro)
        self.camera2chidatread.start()

    def change(self, indx):
        if not self.lis_cam_states[indx]:
            self.listcams[indx] = cv2.VideoCapture(indx)
            self.lis_cam_states[indx] = True
            self.cambutonlist[indx].configure(background='black')

        self.cam_on = True
        self.indexOfCamera2 = indx

    def camera_2_pro(self):

        while True:

            if not self.cam_on:
                continue

            ret, frameXD = self.listcams[self.indexOfCamera2].read(self.indexOfCamera2)

            if ret:
                frameXD = cv2.resize(frameXD, (1100, 700), interpolation=cv2.INTER_AREA)
                frameXD = cv2.cvtColor(frameXD, cv2.COLOR_BGR2RGB)
                frameXD = Image.fromarray(frameXD)
                frameXD = ImageTk.PhotoImage(frameXD)

                # Update the camera feed display
                self.feed2.configure(image=frameXD)
                #self.feed2 = frameXD
                self.image = frameXD
            else:
                self.lis_cam_states[self.indexOfCamera2] = False
                self.cambutonlist[self.indexOfCamera2].configure(background='red')
                self.cam_on = False

    def widgets_child(self):
        self.bg = Image.open("image/pepe.jpg")
        self.bg = self.bg.resize((1536, 864))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.background = tk.Label(self.Frame, image=self.bg, borderwidth=0)

        self.background.place(x=0, y=0)


#Initialize the application
app = Application()
app.mainloop()

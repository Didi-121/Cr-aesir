import tkinter as tk
import time
import threading
import cv2
import numpy as np
from camera import Camera
from PIL import Image
from PIL import ImageTk
from Control_Service import Client
from audio_client import Audio_client

#Server configuration
HOST = "169.254.111.111"
PORT = 5555
JSONPATH = 'Keys.json'
username = "aesir"

IPRASPB = '169.254.111.111'
APORT = 5554

class Application(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.thread = None
        self.wm_title("Aesir interface")
        self.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("1920x1080")

        #self.second_window = VentanaSecundaria(self)
        #Create the main frame with a gray background
        self.mainFrame = tk.Frame(self, background="gray")
        self.mainFrame.pack(fill="both", expand=True)

        self.aClient = Audio_client(HOST, APORT)
        self.audioTrhead = threading.Thread(target=self.aClient.audio_stream_input_UDP, args=())
        self.audioTrhead2 = threading.Thread(target=self.aClient.live_audio, args=())
        self.audioTrhead.start()
        self.audioTrhead2.start()

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

        #Audio client
        self.livea_button = tk.Button(self, text="Listen", fg="gold", bg="black")
        self.livea_button.place(x=40, y=120, width=100, height=30)
        
        self.livea_button.bind('<ButtonPress-1>', self.aClient.a_live_on)
        self.livea_button.bind('<ButtonRelease-1>', self.aClient.a_live_off)

        self.speakbut = tk.Button(self, text="Hear", fg="gold", bg="black")
        self.speakbut.place(x=40, y=80, width=100, height=30)

        self.speakbut.bind('<ButtonPress-1>', self.aClient.audio_On)
        self.speakbut.bind('<ButtonRelease-1>', self.aClient.audio_Off)

        """
        self.audioOn = tk.Button(self, text="Audio on", fg="gold", bg="black", command= self.aClient.audio_On)
        self.audioOn.place(x=40, y=80, width=100, height=30)

        self.audioOff = tk.Button(self, text="Audio off", fg="gold", bg="black", command= self.aClient.audio_Off)
        self.audioOff.place(x=40, y=120, width=100, height=30)
        """

    def onClose(self):
        self.quit()

    def server(self):
        #Start the client thread
        self.server_thread = threading.Thread(target=self.client.main)
        self.server_thread.start()

#Initialize the application
app = Application()
app.mainloop()
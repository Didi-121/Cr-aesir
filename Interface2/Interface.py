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

        #self.second_window = VentanaSecundaria(self)
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


#Initialize the application
app = Application()
app.mainloop()
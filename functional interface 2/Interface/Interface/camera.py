#Code of camera
import cv2
from motion_detector import motion_detector
from QR import QR
from main_hazmat import HAZMAT
import socket
import time
import logging
import threading
from datetime import datetime
import tkinter as tk
from PIL import Image
from PIL import ImageTk

hm = HAZMAT()

class Camera():
    def __init__(self, master, posx, posy):

        self.holder = Image.open("image/holder.jpeg")
        self.holder = self.holder.resize((posx, posy))
        self.holder = ImageTk.PhotoImage(self.holder)

        self.feed = tk.Label(master=master, image=self.holder, borderwidth=0)
        self.feed.pack(padx=80, side="right")
        
        self.image = self.holder

        self.resolutionX = posx
        self.resolutionY = posy

        self.logger = logging.getLogger(__name__)
        
        self.flipping = False
        
        self.texts = ["", "Tracking", "Read QR", "Hazmat", "Flipped"] 
        self.text = self.texts[0]
        self.keys = ["'1'", "'2'", "'3'"]
        self.mode = "D"
        self.flip = False
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.count = 1
        # path for save images (it has to be updated every time it gets on a new device)
        self.images_path = r"B:\functional interface (ESTA ES)\Interface\Interface\images"

        self.Event = threading.Event()
        self.thread = threading.Thread(target=self.main_cam, args=())
        #self.thread.start()
        
        self.sens = tk.StringVar()
        
        self.scroll = tk.Scale(master, from_=1, to=100, variable=self.sens)
        
        self.button = tk.Button(master, text="Start cam", width=100)
        self.button.place(x=1400, y=30, width=100)
        
        self.link = tk.Button(master, text="Open link", width=100)
        self.linked = False
        self.screenshot = False
        
        self.camID = tk.StringVar()
        self.camID.set("0")
        
        self.index = tk.Entry(master, textvariable=self.camID, highlightthickness=4)
        self.index.place(x=1400, y=60, width=100)
        
        self.button.bind('<Button>', self.startNewCam)
        self.link.bind('<Button>', self.open)
        
        
        self.sens.set(50)

        #self.label = tk.Label(self, text="Sensitivity:", foreground="white", font=("Arial", 15))


    def main_cam(self):

        self.camara = cv2.VideoCapture(1)

        self.cam = cv2.VideoCapture(int(self.camID.get()))
        self.button.configure(text="Disconnect cam")
        self.button.bind('<Button>', self.stopCam)
        self.index.configure(state="disabled")

        ret, frame1 = self.cam.read()
        ret, frame2 = self.cam.read()

        while self.cam.isOpened():
            #asyncio.run(self.revc())
            # Check camera mode
            
            if self.mode == "Q":
                frame1 = QR(frame1, self.font, self.linked)
                
                if self.linked:
                    self.linked = False
                    
                self.text = self.texts[2]
            elif self.mode == "M":
                frame1 = motion_detector(self.cam).frames(frame1, frame2, 101 - int(self.sens.get()))
                self.text = self.texts[1]
            elif self.mode == "H":
                frame1 = hm.draw(frame1)
                self.text = self.texts[3]
            else:
                self.text = self.texts[0]

            # Show image of camera
            
            cv2.putText(frame1, self.text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 100), 4)
            
            if self.flip:
                cv2.putText(frame1, self.texts[4], (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 100), 4)



            if not self.Event.is_set():
                #self.logger.info("loop")
                #try:
                
                if self.screenshot:
                    self.take_picture(frame1)   
                self.screenshot = False 
                
                frame1 = cv2.resize(frame1, (self.resolutionX, self.resolutionY), interpolation=cv2.INTER_AREA)
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                frame1 = Image.fromarray(frame1)
                frame1 = ImageTk.PhotoImage(frame1)

                                       
                    
                self.feed.configure(image=frame1)
                    
                 
                    
                self.image = frame1


                frame1 = frame2
                #except:
                #    break

                ret, frame2 = self.cam.read()
            else:
                try:
                    self.feed.config(image=self.holder)
                    self.image = self.holder
                    break
                except:
                    break

            # Check keys pressed
            
            if self.flipping:
            
                self.flipping = False
                if self.flip == True:
                    self.flip = False
                    time.sleep(.1)
                else:
                    self.flip = True
                    time.sleep(.1)
            if self.flip:
                frame2 = cv2.rotate(frame2, cv2.ROTATE_180)

            # Switch to close camera
        self.logger.info("released")
        self.cam.release()

    def change(self, key):
        
        #self.label.pack_forget()
        self.scroll.place_forget()
        self.link.place_forget()
        
        if key == 49:
            self.mode = 'D'
            return
        
        if key == 50:
            self.mode = 'M'
            
            #self.label.pack(side="top", pady=10)
            self.scroll.place(x=1400, y=332)
            
            return
        
        if key == 51:
            self.mode = 'Q'
            self.link.place(x=1320, y=150, width=100)
            return
        
        if key == 52:
            self.mode = 'H'
            
            return
        
        if key == 53:
            self.flipping = True
            
            if self.mode == "M":
                self.scroll.place(x=1400, y=332)
                return
            if self.mode == "Q":
                self.link.place(x=1320, y=150, width=100)
            return
        
        
    def take_picture(self, frame):
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S")
        
        cv2.imwrite(self.images_path + "/image_" + today_date + ".jpg", frame)
        #("Photo taken")


    def stopCam(self, event = ''):
        self.Event.set()
        self.index.configure(state="normal")
        self.button.configure(text="Open cam")
        self.button.bind('<Button>', self.startNewCam)

    def startNewCam(self, event):
        
        self.button.configure(text="Opening cam")
        self.button.bind('<Button>', self.nothing)

        self.thread = threading.Thread(target=self.main_cam, args=())
        
        if self.thread.is_alive():
            self.thread.join()
        
        if self.Event.is_set():
            self.Event.clear()
        
        self.thread.start()
        
    def nothing(self, event):
        pass
    
    def open(self, event):
        self.linked = True
        
    def ss(self):
        self.screenshot = True

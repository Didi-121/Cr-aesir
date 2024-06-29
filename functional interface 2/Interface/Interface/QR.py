#Code that reads qr
import cv2
import numpy as np
#from pyzbar import pyzbar
from pyzbar import pyzbar
import webbrowser
from datetime import datetime



#path for save images (it has to be updated every time it gets on a new device)
images_path = r"B:\functional interface (ESTA ES)\Interface\Interface\images"

images = {True, 1}

count = 0

def QR(image,font,open):
    #Read QR
    barcodes = pyzbar.decode(image)
    
    squares = image

    for barcode in barcodes:
        
        (x,y,w,h) = barcode.rect
        squares = cv2.rectangle(squares, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        
		# the barcode data is a bytes object so if we want to draw it
		# on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
		# draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(squares, text, (x, y - 10),
            font, 0.5, (0, 0, 255), 2)
        
        if open:
            webbrowser.open(barcodeData)
        
        if barcodeData not in images:
            images.add(barcodeData)
            take_picture(barcodeData, squares)
    
    
    return squares

def take_picture(name, frame):
    today_date = datetime.now().strftime("%m%d%Y-%H%M%S")
    
    
    with open(images_path + "/image" + str(count) + "_" + today_date + ".txt", "w") as f:
        f.write(name)
    
    cv2.imwrite(images_path + "/image" + str(count) + "_" + today_date + ".jpg", frame)
    #("Photo taken")
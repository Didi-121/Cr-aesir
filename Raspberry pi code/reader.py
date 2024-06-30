import serial


# dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1
#ttyACM0 or ttyUSB0
try:
    arduino = serial.Serial("/dev/ttyUSB0",9600)
    arduino.flushInput()
    print("Arduino connected")
except:
     print("failed to connect with arduino")


arduino.bytesize = serial.EIGHTBITS 
arduino.stopbits = serial.STOPBITS_ONE #number of stop bits
arduino.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
arduino.dsrdtr = True       #disable hardware (DSR/DTR) flow control
     
print("Esperando mensajes...")
while True:
    if arduino.in_waiting > 0 :
        recieved = arduino_message = str(arduino.readline())
        recieved = recieved[2:][:-5]
        print(recieved)


#arduino_message = str(arduino.readline())

#arduino.read(arduino.in_waiting).decode('utf-8').rstrip()
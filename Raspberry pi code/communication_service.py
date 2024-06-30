import json 
import serial
import socket 
import time
import threading 
import logging
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

class Messenger():

    def __init__(self , JSON_PATH, UDP_IP, PORT, serial_device, baud_rate):

        self.logger = logging.getLogger(__name__)

        with open(JSON_PATH) as jsonfile:
            keysDictionary = json.load(jsonfile)
        
        self.keysInstructions = keysDictionary

        self.host = UDP_IP

        self.port = PORT

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind( (self.host, self.port) )

        
        self.client_conected =  False

        self.serialDevice = serial_device
        self.baud_rate = baud_rate
        self.arduino_conected = False

        self.main()
            

    def client_connect(self):

        self.server.listen(1)

        while True:

            self.client, self.addr = self.server.accept()
            self.client.send("USERNAME?".encode())  
            
            
            while True:

                self.username = self.client.recv(1024).decode()
                
                if self.username == "aesir":
                    answer  = (f"Conection established at {self.addr} and port: {self.port}")
                    print(f"Conection established with the client: {self.username}") 
                    self.client.send(answer.encode())
                    self.client_conected = True
                    break

                else:

                    answer  = ("Invalid user")
                    self.client.send(answer.encode())
                    self.client.close()
                    self.client_conected = False
                    break

            if self.client_conected:
                    break
            
    def arduino_connect(self):
        try:
            self.arduino = serial.Serial(self.serialDevice,self.baud_rate)
            self.arduino.dsrdtr = True       #disable hardware (DSR/DTR) flow control
            self.arduino.flushInput()
            self.arduino.flushOutput()
            
        except serial.serialutil.SerialException :
            logging.warning("The arduino isnt conected ")

    def arduino_read(self):

        while self.arduino_conected:

            if self.arduino.in_waiting > 0 or True:

                arduino_message = str(self.arduino.readline())
                arduino_message = arduino_message[2:][:-5]

            time.sleep(0.001)


    def message_build(self, information ):

        key_state = information[0]
        key = information[1:]
        
        if self.keysInstructions.get(key):
            
            keyDefinition = self.keysInstructions.get(key)    
            instructionType = keyDefinition[0]

        else:
            return 
        
        if key_state == 'T': 

            if instructionType == 'DC':

                action = keyDefinition[1] 
                message = f"D{action}"
                message = message.encode("utf-8")
                return message
            
            elif instructionType == 'SERVO':
                action = keyDefinition[1]
                

                if (action == 'F' or action == 'B'):
                    id = hex(keyDefinition[2])[2:].upper()
                    id = "0" * (2 - (len(str(id)))) + str(id)
                    message = f"S{action}{id}"
                    message = message.encode("utf-8")
                    return message 
                
                elif (action == 'P'):
                    id = hex(keyDefinition[2])[2:].upper()
                    id = "0" * (2 - (len(str(id)))) + str(id)
                    position = hex(keyDefinition[3])[2:].upper()
                    position = "0" * (3 - (len(str(position)))) + str(position)
                    message= f"S{action}{id}{position}"
                    message = message.encode("utf-8")
                    return message
                
            elif (instructionType == 'PREPOSITION'):
                comands = keyDefinition[1]
                comands= comands.encode("utf-8")
                return comands
            
            elif (instructionType == "OS"):
                action = keyDefinition[1]

                if action == "exit":
                    self.client.close()
                    raise ValueError("xd ndms queria cerrar el programa")
                    sys.exit()

                else:
                    return "invalid"
            
            else:
                return "invalid"
             
        
        elif key_state == 'F':

            if instructionType == 'DC':
                message = "D"
                message = message.encode("utf-8")
                return message
            
            elif instructionType == 'SERVO':
                action = keyDefinition[1]
                id = hex(keyDefinition[2])[2:].upper()
                id = "0" * (2 - (len(str(id)))) + str(id)

                if (action == 'F' or action == 'B'):
                    message  = f"S{id}"
                    message = message.encode("utf-8")
                    return message   
                
            else:
                return "invalid"
            
        else:
            return "invalid"
    
    def client_read(self):

        while  True: #self.client_conected:

            try:
            
                client_message = self.client.recv(2048).decode()

                logging.debug(client_message)

                arduino_instruction = self.message_build(client_message)

                logging.debug(arduino_instruction)

                self.arduino.write(arduino_instruction)
                
            except TypeError:
                logging.debug("Maybe its an instruction for the os ")

            except ConnectionResetError:
                self.client_conected = False
                self.client.close()
                logging.warning("The client was desconected ")
                self.client_connect()
            
            finally:
                time.sleep(0.001)

    def main(self):

        self.client_connect()
        self.arduino_connect()

        t1 = threading.Thread(target = self.arduino_read )
        t2 = threading.Thread(target = self.client_read )
        
        t1.start()
        t2.start()

        
json_dir = "commands.json"
host = "169.254.111.111"
port = 5555
serialDevice = "/dev/ttyUSB0"
baudRate = 9600

comunicador = Messenger(json_dir, host, port, serialDevice, baudRate)
comunicador.main()

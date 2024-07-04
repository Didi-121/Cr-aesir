import socket
import time
from pynput import keyboard as kb
import socket
import json
import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s: %(message)s')


class Client:
    def __init__(self, _HOST, _PORT, _username, x ):

        self.logger = logging.getLogger(__name__)

        self.host = _HOST
        self.port = _PORT
        self.username = _username
        
        actual_path = os.path.dirname(os.path.abspath(__file__))
        file_name = "keys.json"
        self.json_path = os.path.join(actual_path, file_name)

        with open(self.json_path) as bruteKeys:
            self.os_keys = json.load(bruteKeys)

        self.usedKeys = []  # list with the keys that were pressed
        self.keyState = []  # list with the bool state of the pressed key
        self.KEYS = [self.usedKeys, self.keyState]

        self.usedKeys.append('`')
        # idk why but the first key in the list continue with spam, so choose a key that you wont use
        self.keyState.append(True)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = 30
        self.server_socket.settimeout(self.timeout)
        self.camera_function = x

    def try_conection(self):

        while True:

            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.connect((self.host, self.port))

            except ConnectionRefusedError:
                logging.warning("conection refused ")
                self.conected = False
                self.server_socket.close()
                time.sleep(3)
                continue

            except  ConnectionAbortedError:
                logging.warning("conection aborted ")
                self.conected = False
                self.server_socket.close()
                time.sleep(3)
                continue

            except WindowsError:
                logging.warning("No available host ")
                self.conected = False
                self.server_socket.close()
                time.sleep(3)
                continue

            comand = self.server_socket.recv(1024).decode()

            if comand == "USERNAME?":
                self.server_socket.send(self.username.encode())
                confirmation = self.server_socket.recv(1024).decode()
                logging.warning(confirmation)
                self.conected = True

                break

        # this function search an element in a list, it return the index of the elemnt or false if its not in the list

    def lookFor(self, x, list):
        try:
            x = list.index(x)
            return x

        except ValueError:
            return False

            # this function compare 2 list and return the element that is different, or return None if they are equal

    def comparator(self, oldList, newList):
        y = 0
        for x in oldList:

            if x == newList[y]:
                y += 1

            else:
                return y

    # this function start when a key is pressed
    def press(self, key):
        try:

            if self.conected:

                # format the key
                key = str(key)
                key = key.replace("'", "")
                key = key.replace("<", "")
                key = key.replace(">", "")

                # If the key was already used
                if self.lookFor(key, self.usedKeys):

                    # While the key is pressed, this functions repeats, so we avoid spam creating a list that changes the state of the pressed key
                    oldList = list(self.KEYS[1])

                    # we get the index of the key and make it true
                    key_index = self.KEYS[0].index(key)
                    self.KEYS[1][key_index] = True

                    # if there is a change between the lists, then the function can enter
                    if self.comparator(oldList, self.KEYS[1]):

                        if not (self.os_keys.get(key)):

                            message = 'T'
                            message += key
                            message = message.encode()
                            self.server_socket.send(message)
                            logging.debug(message)

                        else:
                            self.camera_function(self.os_keys.get(key))

                # the key wasnt used we add it to the list
                else:
                    self.KEYS[0].append(key)
                    self.KEYS[1].append(True)

                    message_destiny = self.os_keys.get(key)

                    if message_destiny == "os":
                        logging.debug("somethin in the laptop")

                    else:
                        message = 'T'
                        message += key
                        message = message.encode()
                        self.server_socket.send(message)
                        logging.debug(message)

        except ConnectionRefusedError:
            logging.warning("conection refused ")
            self.conected = False
            self.server_socket.close()
            self.try_conection()


        except  ConnectionAbortedError:
            logging.warning("conection aborted ")
            self.conected = False
            self.server_socket.close()
            self.try_conection()


        except WindowsError:
            logging.warning("No available host ")
            self.conected = False
            self.server_socket.close()
            self.try_conection()

    # this function start when a key is released
    def release(self, key):

        try:

            if self.conected:

                # format the key
                key = str(key)
                key = key.replace("'", "")
                key = key.replace("<", "")
                key = key.replace(">", "")

                # We use the same method as in the pressed keys to avoid spam
                if self.lookFor(key, self.usedKeys):

                    pressedKey = self.KEYS[0].index(key)
                    self.KEYS[1][pressedKey] = False

                    if not self.os_keys.get(key):
                        message = 'F'
                        message += key
                        message = message.encode()
                        self.server_socket.send(message)
                        logging.debug(message)
                    else:
                        pass

        except ConnectionRefusedError:
            logging.warning("conection refused ")
            self.conected = False
            self.server_socket.close()
            

        except  ConnectionAbortedError:
            logging.warning("conection aborted ")
            self.conected = False
            self.server_socket.close()
            

        except WindowsError:
            logging.warning("No available host ")
            self.conected = False
            self.server_socket.close()
            

    def main(self):

        self.try_conection()

        if self.conected:
            with kb.Listener(self.press, self.release) as listener:
                listener.join()

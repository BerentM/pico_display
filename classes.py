from utime import time_ns
from machine import I2C, Pin
from time import sleep, time
from pico_i2c_lcd import I2cLcd

class Screen:
    def __init__(self):
        i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
        I2C_ADDR = i2c.scan()[0]
        self.lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

    def clear(self):
        """
        Clears LCD display.
        """
        self.lcd.clear()
        
    def backlight(self):
        return self.lcd.backlight
        
    def toggle(self):
        """
        Toggles on/off screen backlight.
        """
        if self.lcd.backlight:
            self.lcd.backlight_off()
        else:
            self.lcd.backlight_on()
            
    def display(self, text):
        """
        Put text on display.
        """
        self.lcd.clear()
        if not self.lcd.backlight:
            self.lcd.backlight_on()
        self.lcd.putstr(text)
        


class Storage:
    def __init__(self, path="storage.csv"):
        self.path = path
        
    def clear(self):
        """
        Clear data in storage file.
        """
        with open(self.path, "w") as f:
            pass

    def add_row(self, content:list, delimiter:str):
        """
        Append row to storage file.
        """
        output = delimiter.join(content)
        with open(self.path, "a") as f:
            f.write(output+"\n")
            
    def size(self):
        """
        Check size of Storage file.
        """
        with open(self.path, "r") as f:
            return len(f.readlines())
    
    def get_row(self, row_num=None):
        """
        Return specified (default last) row.
        """
        if row_num is None:
            row_num = self.size()-1
        if row_num < 0:
            return "NO DATA!"
        with open(self.path, "r") as f:
            return f.readlines()[row_num]


class Button:
    def __init__(self, btn_id, gpio):
        self.btn = Pin(gpio, Pin.IN, Pin.PULL_DOWN)
        self.btn_id = btn_id
        
    def __repr__(self):
        return f"Button {self.btn_id=}"
    
    def active(self):
        """
        Return 1 if button was pressed, then released.
        """
        if self.btn.value():
            first = self.btn.value()
            sleep(0.1)
            if first != self.btn.value():
                return 1
        return 0


class Board:
    def __init__(self):
        self.buttons = (
            Button(1, 19),
            Button(2, 18),
            Button(3, 17),
            Button(4, 16),
            )
        self.screen = Screen()
        self.last_update = time()
        self.active_screen = 0
        
    def update(self, screen_number):
        """
        Update Board state.
        """
        self.active_screen = screen_number
        self.last_update = time()
        
class Timer:
    def __init__(self):
        self._elapsed_time = 0
    
    def start(self):
        # if self._elapsed_time:
        #     # TODO: implement pause
        #     pass
        # else:
        self.start_time = time_ns()

    def elapsed(self):
        self._elapsed_time = time_ns() - self.start_time
        return self._elapsed_time

    def stop(self):
        self._elapsed_time = time_ns() - self.start_time
        return self._elapsed_time
        


class Task:
    def __init__(self, name, category = 'misc'):
        self.category = category
        self.name = name        
        self.active = False

    def __repr__(self):
        return f"{self.category}:{self.name}"

    def start(self):
        self.active = True
        self.tim = Timer()
        self.tim.start()

    def status(self):
        return self.tim.elapsed()

    def stop(self):
        self.active = False
        self.tim.stop()


class Tasks:
    def __init__(self, task_list=["work", "fun", "focus"]):
        self.list = [Task(task) for task in task_list]
        self.current_index = 0
        self.current_task = self.list[self.current_index]
    
    def next_task(self) -> Task:
        if self.current_index == len(self.list)-1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.current_task = self.list[self.current_index]
        return self.current_task

    def prev_task(self) -> Task:
        if self.current_index == 0:
            self.current_index = len(self.list)-1
        else:
            self.current_index -= 1
        self.current_task = self.list[self.current_index]
        return self.current_task
from machine import I2C, Pin
from utime import sleep, time

from pico_i2c_lcd import I2cLcd


class Screen:
    """
    Class responsible for all display actions.
    """
    def __init__(self):
        i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
        I2C_ADDR = i2c.scan()[0]
        self.lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
        self._cur_displayed = ''

    def clear(self):
        """
        Clears LCD display.
        """
        self.lcd.clear()
        
    def backlight(self):
        """Check backlight state.

        Returns:
            (bool): Is backlight on?
        """
        return self.lcd.backlight
        
    def toggle(self):
        """
        Toggles on/off screen backlight.
        """
        if self.lcd.backlight:
            self.lcd.backlight_off()
        else:
            self.lcd.backlight_on()
            
    def display(self, text:str, switch_light=True):
        """
        Put text on display.
        """
        if not self.lcd.backlight and switch_light:
            self.lcd.backlight_on()
        if self._cur_displayed != text:
            self.lcd.clear()
            self.lcd.putstr(text)
            self._cur_displayed = text
        


class Storage:
    """
    Class responsible for data storage.
    """
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
        Append new row to storage file.

        Args:
            content (list): List of data, that will be saved.
            delimiter (str): Data is stored in csv file, provide delimiter for easier parsing.
        """
        content = [str(elem) for elem in content]
        output = delimiter.join(content)
        with open(self.path, "a") as f:
            f.write(output+"\n")
            
    def size(self):
        """
        Check size of Storage file.
        """
        with open(self.path, "r") as f:
            return len(f.readlines())
    
    def get_row(self, row_num:int=None) -> str:
        """Return specified (default last) row.

        Args:
            row_num (int, optional): Row number from file. Defaults to None.

        Returns:
            str: Exact row_num row from storage file.
        """
        
        if row_num is None:
            row_num = self.size()-1
        if row_num < 0:
            return "NO DATA!"
        with open(self.path, "r") as f:
            return f.readlines()[row_num]

    def del_row(self, row_num:int=None):
        """Delete row from storage.

        Args:
            row_num (int, optional): Row to delete. Defaults to None.
        """
        if row_num is None:
            row_num = self.size()-1
        if row_num < 0:
            return
        with open(self.path, "r") as f:
            lines = f.readlines()

        output = lines[:row_num]
        output.extend(lines[row_num+1:])
        with open(self.path, "w") as f:
            for row in output:
                f.write(row)


class Button:
    """
    Class for all of the all of the button actions and state.
    """
    def __init__(self, btn_id, gpio):
        self.btn = Pin(gpio, Pin.IN, Pin.PULL_DOWN)
        self.btn_id = btn_id
        
    def __repr__(self):
        return f"Button {self.btn_id=}"
    
    def active(self) -> int:
        """
        Check if button is active

        Returns:
            int: 1 when button was pressed
        """
        if self.btn.value():
            first = self.btn.value()
            sleep(0.1)
            if first != self.btn.value():
                return 1
        return 0


class Board:
    """
    Board state and all of the elements of it.
    """
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
        
    def update(self, screen_number: int):
        """Update Board state.

        Args:
            screen_number (int): Currently active screen.
        """
        self.active_screen = screen_number
        self.last_update = time()
        
class Timer:
    def __init__(self):
        self.active = True
        self._elapsed_time = 0
        self.prev_refresh = -1
        self.start_time = time()
        self.intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('h', 3600),    # 60 * 60
            ('m', 60),
            ('s', 1),
        )

    def __repr__(self):
        return f"{self.display_time(self._elapsed_time)}"

    def display_time(self, seconds:int, granularity=2):
        """Format seconds into higher level values.

        Args:
            seconds (int): Seconds for conversion.
            granularity (int, optional): How many elements should be returned. Defaults to 2.

        Returns:
            (str): Formated seconds.
        """
        result = []

        for name, count in self.intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1 and name != 's':
                    name = name.rstrip('s')
                result.append(f"{value}{name}")
        return ':'.join(result[:granularity]) 
        
    def elapsed(self):
        """
        Update Timer state.

        Returns:
            (int): How many seconds elapsed from init.
        """
        self._elapsed_time = time() - self.start_time
        return self._elapsed_time

    def restart(self):
        """
        Restart Timer
        """
        self.__init__()

    def refresh(self, refresh_sec: int):
        """
        Update Timer state.

        Args:
            refresh_sec (int): At which second, starting from init timer was refreshed.
        """
        self.prev_refresh = refresh_sec

    def toggle(self):
        """
        Toggle Timer state.
        Used for pause/resume.
        """
        if self.active:
            self.active = False
        else:
            self.restart()



class Task:
    """
    Single task class.
    """
    def __init__(self, category, name):
        self.category = category
        self.name = name        
        self.active = False

    def __repr__(self):
        return f"{self.category}:{self.name}"

    def start(self):
        self.active = True
        self.tim = Timer()

    def status(self):
        return self.tim.elapsed()

    def stop(self):
        self.active = False


class Tasks:
    """
    Keep all Task class objects in one place.
    """
    def __init__(self, task_list):
        self.list = []
        for tup in task_list:
            category, name = tup
            self.list.append(Task(category, name))
        self.current_index = 0
        self.current_task = self.list[self.current_index]
    
    def next_task(self) -> Task:
        """Move to next Task in list.

        Returns:
            Task: Next Task, becomes active immediately.
        """
        if self.current_index == len(self.list)-1:
            self.current_index = 0
        else:
            self.current_index += 1
        self.current_task = self.list[self.current_index]
        return self.current_task

    def prev_task(self) -> Task:
        """Move to previous Task in list.

        Returns:
            Task: Previous Task, becomes active immediately.
        """
        if self.current_index == 0:
            self.current_index = len(self.list)-1
        else:
            self.current_index -= 1
        self.current_task = self.list[self.current_index]
        return self.current_task

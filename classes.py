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
        
    def clear(self) -> str:
        """
        Clear data in storage file.
        """
        with open(self.path, "w") as f:
            pass

    def add_row(self, content:list, delimiter:str) -> str:
        """
        Append row to storage file.
        """
        output = delimiter.join(content)
        with open(self.path, "a") as f:
            f.write(output+"\n")
            
    def size(self):
        with open(self.path, "r") as f:
            return len(f.readlines())
    
    def get_row(self, row_num=None):
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

    def action(self, action, args=None):
        """
        Most likely unnecesary.
        """
        return action(*args) if args else action()


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
        self.active_screen = screen_number
        self.last_update = time()

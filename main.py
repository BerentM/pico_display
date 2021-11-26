from time import sleep,localtime,time
from classes import Board, Storage

BOARD = Board()
BTN = BOARD.buttons
SCREEN = BOARD.screen

STORAGE = Storage()
screen_timeout = 10

def time_now() -> str:
    """
    Returns formatted timestamp.
    Implemented due to lack of strftime func.
    """
    lt = localtime()
    t = []
    for elem in lt:
        t.append('0'+str(elem) if elem < 10 else str(elem))
    return f"{t[0]}-{t[1]}-{t[2]}\n{t[3]}:{t[4]}:{t[5]}"

# MAIN LOOP
while True:
    if SCREEN.backlight():
        if time() - BOARD.last_update > screen_timeout:
            BOARD.update(BOARD.active_screen)
            SCREEN.toggle()
    if BTN[0].active():
        BOARD.update(0)
        SCREEN.toggle()
    if BTN[1].active():
        BOARD.update(1)
        STORAGE.clear()
        SCREEN.display("wyczyszczono\nwpisy")
    if BTN[2].active():
        BOARD.update(2)
        STORAGE.add_row(['kol', 'kol2','kol3'], ';')
        SCREEN.display("dodano wpis")
    if BTN[3].active():
        BOARD.update(3)
        SCREEN.display(str(STORAGE.get_row()))


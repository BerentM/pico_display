from time import localtime, time

from classes import Board, Storage, Tasks, Timer

BOARD = Board()
BTN = BOARD.buttons
SCREEN = BOARD.screen

TASKS = Tasks(
    task_list=[
        ("work", "code"),
        ("work", "mail"),
        ("work", "meetings"),
        ("work", "ideas"),
        ("fun", "yt"),
        ("fun", "games"),
    ]
)

STORAGE = Storage()
tim = Timer()

screen_timeout = 20

def time_now() -> str:
    """
    Returns formatted timestamp.
    Implemented due to lack of strftime func.
    """
    lt = localtime()
    t = []
    for elem in lt:
        t.append('0'+str(elem) if elem < 10 else str(elem))
    return f"   {t[2]}.{t[1]}.{t[0]}\n     {t[3]}:{t[4]}"

# MAIN LOOP
while True:
    refresh_frequency = 5
    tim_elapsed = tim.elapsed()
    tim_refresh = tim_elapsed % refresh_frequency == 0 and tim_elapsed != tim.prev_refresh
    # GENERAL LOGIC
    if SCREEN.backlight():
        if time() - BOARD.last_update > screen_timeout:
            BOARD.update(BOARD.active_screen)
            SCREEN.toggle()
    
    # BUTTON ACTION
    if BTN[0].active():
        BOARD.update(0)
        SCREEN.display(time_now())
    if BTN[1].active():
        BOARD.update(1)
        s = TASKS.prev_task()
        SCREEN.display(str(s))
        tim.restart()
    if BTN[2].active():
        BOARD.update(2)
        s = TASKS.next_task()
        SCREEN.display(str(s))
        tim.restart()
    if BTN[3].active():
        BOARD.update(3)
        try:
            task, t = STORAGE.get_row().split(";")
            SCREEN.display(str(task)+"\n"+str(t))
        except ValueError:
            SCREEN.display(str(TASKS.current_task)+"\n"+str(tim))

    if tim_elapsed != tim.prev_refresh and BOARD.active_screen == 0:
        SCREEN.display(time_now(), False)
        tim.refresh(tim_elapsed)
    elif tim_refresh and BOARD.active_screen == 3:
        try:
            task, t = STORAGE.get_row().split(";")
            SCREEN.display(str(task)+"\n"+str(t), False)
        except ValueError:
            SCREEN.display(str(TASKS.current_task)+"\n"+str(tim), False)
        tim.refresh(tim_elapsed)
    
    if tim_refresh and tim_elapsed >= refresh_frequency:
        last_row = STORAGE.get_row().split(';')
        if last_row[0] != str(TASKS.current_task):
            STORAGE.add_row([TASKS.current_task, tim_elapsed], ";")
        else:
            STORAGE.del_row()
            STORAGE.add_row([TASKS.current_task, int(last_row[1])+refresh_frequency], ";")

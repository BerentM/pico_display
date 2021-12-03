from time import localtime, time

from classes import Board, Storage, Tasks, Timer

BOARD = Board()
BTN = BOARD.buttons
SCREEN = BOARD.screen

TASKS = Tasks(
    task_list=[
        ("work", "code"),
        ("work", "writing"),
        ("work", "meetings"),
        ("work", "ideas"),
        ("fun", "yt"),
        ("fun", "games"),
        ("misc", "web"),
        ("other", "other"),
    ]
)

STORAGE = Storage()
tim = Timer()
refresh_frequency = 5
tim_elapsed, tim_refresh = 0,0

screen_timeout = 20

def time_now() -> str:
    """
    Format time.localtime.
    Implemented due to lack of strftime func.

    Returns:
        str: formated text
    """
    lt = localtime()
    t = []
    for elem in lt:
        t.append('0'+str(elem) if elem < 10 else str(elem))
    return f"   {t[2]}.{t[1]}.{t[0]}\n     {t[3]}:{t[4]}"

def display_task_time() -> str:
    """Nicely formatted task & time.

    Returns:
        str: formated text
    """
    # TODO: simplify that spaghetti
    try:
        task, t = STORAGE.get_row().split(";")
        if task == str(TASKS.current_task):
            if tim.active:
                return str(task)+"\n"+str(tim.display_time(int(t)))
            else:
                return str(task)+"\n"+str("continue")
        else:
            if tim.active:
                return str(TASKS.current_task)+"\n"+str(tim)
            else:
                return str(TASKS.current_task)+"\n"+str("start")
    except ValueError:
        return str(TASKS.current_task)+"\n"+str(tim)
    
def refresh_func(refresh_frequency):
    tim_elapsed = tim.elapsed()
    tim_refresh = tim_elapsed % refresh_frequency == 0 and tim_elapsed != tim.prev_refresh
    return tim_elapsed, tim_refresh

# MAIN LOOP
while True:
    if tim.active:
        tim_elapsed, tim_refresh = refresh_func(refresh_frequency)
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
        if BOARD.active_screen != 0:
            s = TASKS.prev_task()
            tim.restart()
        BOARD.update(1)
        SCREEN.display(display_task_time())
    if BTN[2].active():
        if BOARD.active_screen != 0:
            s = TASKS.next_task()
            tim.restart()
        BOARD.update(2)
        SCREEN.display(display_task_time())
    if BTN[3].active():
        if BOARD.active_screen != 0:
            tim.toggle()
            if tim.active is False:
                tim_elapsed, tim_refresh = refresh_func(refresh_frequency)
            SCREEN.display(display_task_time())
        else:
            # TODO: jump to previously active task - read it from file
            # if file is empty, display first task from list
            BOARD.update(1)
            SCREEN.display(display_task_time())

    if tim_elapsed != tim.prev_refresh and BOARD.active_screen == 0:
        SCREEN.display(time_now(), False)
        tim.refresh(tim_elapsed)

    elif tim_refresh and tim.active and BOARD.active_screen in (1,2):
        SCREEN.display(display_task_time(), False)
        tim.refresh(tim_elapsed)
    
    if tim_refresh and tim_elapsed >= refresh_frequency and tim.active and tim_elapsed >= 5:
        last_row = STORAGE.get_row().split(';')
        if last_row[0] != str(TASKS.current_task):
            STORAGE.add_row([TASKS.current_task, tim_elapsed], ";")
        elif last_row[0] == str(TASKS.current_task):
            STORAGE.del_row()
            STORAGE.add_row([TASKS.current_task, int(last_row[1])+refresh_frequency], ";")
        tim.refresh(tim_elapsed)

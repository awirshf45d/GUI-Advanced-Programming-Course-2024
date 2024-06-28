import curses
from src.auth import login, register, guest_login
from src.menu import show_menu

def main_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    
    menu_items = ["Login", "Register", "Login as Guest", "View Menu", "Exit"]
    current_row = 0
    
    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, row in enumerate(menu_items):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    print_menu(stdscr, current_row)
    
    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                login(stdscr)
            elif current_row == 1:
                register(stdscr)
            elif current_row == 2:
                guest_login(stdscr)
            elif current_row == 3:
                show_menu(stdscr)
            elif current_row == 4:
                break
        print_menu(stdscr, current_row)

def run_curses():
    curses.wrapper(main_menu)

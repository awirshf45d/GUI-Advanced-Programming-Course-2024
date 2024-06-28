import curses
users = {}

def login(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - 10, "Username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2 + 1).decode('utf-8')
    stdscr.addstr(h//2 - 1, w//2 - 10, "Password: ")
    password = stdscr.getstr(h//2 - 1, w//2 + 1).decode('utf-8')
    curses.noecho()

    if username in users and users[username] == password:
        stdscr.addstr(h//2, w//2 - 10, f"Welcome back, {username}!")
    else:
        stdscr.addstr(h//2, w//2 - 10, "Invalid username or password.")
    stdscr.addstr(h//2 + 3, w//2 - 10, "Press any key to return to main menu.")
    stdscr.refresh()
    stdscr.getch()

def register(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - 15, "Choose a username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2 + 4).decode('utf-8')
    if username in users:
        stdscr.addstr(h//2 - 1, w//2 - 10, "Username already exists.")
        stdscr.addstr(h//2 + 3, w//2 - 10, "Press any key to return to main menu.")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.addstr(h//2 - 1, w//2 - 15, "Choose a password: ")
    password = stdscr.getstr(h//2 - 1, w//2 + 4).decode('utf-8')
    curses.noecho()
    users[username] = password
    stdscr.addstr(h//2, w//2 - 15, f"User {username} registered successfully!")
    stdscr.addstr(h//2 + 3, w//2 - 10, "Press any key to return to main menu.")
    stdscr.refresh()
    stdscr.getch()

def guest_login(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2, w//2 - 10, "Logged in as Guest.")
    stdscr.addstr(h//2 + 3, w//2 - 10, "Press any key to return to main menu.")
    stdscr.refresh()
    stdscr.getch()

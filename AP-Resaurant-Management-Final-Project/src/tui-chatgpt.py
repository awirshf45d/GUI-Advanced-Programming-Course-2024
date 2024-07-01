import curses
import curses.ascii
import time
from db.models import User
from db.db import close_connection, connect_to_database

def launch():
    curses.wrapper(start_menu)

def start_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    
    menu_items = [
        {"label": "Login", "func": login},
        {"label": "Register", "func": register},
        {"label": "View Menu", "func": show_menu},
        {"label": "Exit", "func": exit_program}
    ]
    current_row = 0

    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, item in enumerate(menu_items):
            x = w // 2 - len(item["label"]) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item["label"])
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item["label"])
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    print_menu(stdscr, current_row)
    
    while True:
        key = stdscr.getch()
        if key in [10, 13]:
            if current_row == len(menu_items) - 1:
                exit_program(stdscr)
            else:
                menu_items[current_row]["func"](stdscr)
            return
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1

        print_menu(stdscr, current_row)

def load_dashboard(stdscr, user):
    curses.curs_set(0)
    stdscr.keypad(True)

    menu_items = [
        {"label": "Food Menu", "func": show_menu},
        {"label": "Logout and Exit", "func": logout}
    ]
    if user.isAdmin:
        menu_items.insert(0, {"label": "Admin Panel", "func": admin_panel})

    current_row = 0

    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 4, w // 4, user.username)
        if user.isAdmin:
            stdscr.addstr(h // 4, w // 4 + len(user.username) + 2, "ADMIN", curses.A_BOLD)

        for idx, item in enumerate(menu_items):
            x = w // 2 - len(item["label"]) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item["label"])
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item["label"])
        stdscr.refresh()

    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()
        if key in [10, 13]:
            menu_items[current_row]["func"](stdscr, user)
            return
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1

        print_menu(stdscr, current_row)

def admin_panel(stdscr, user):
    curses.curs_set(0)
    stdscr.keypad(True)
    menu_items = [
        {"label": "Users", "func": show_users},
        {"label": "Logout and Exit", "func": logout}
    ]

    current_row = 0

    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 4, w // 4, user.username)
        if user.isAdmin:
            stdscr.addstr(h // 4, w // 4 + len(user.username) + 2, "ADMIN", curses.A_BOLD)

        for idx, item in enumerate(menu_items):
            x = w // 2 - len(item["label"]) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item["label"])
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item["label"])
        stdscr.refresh()
    
    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()
        if key in [10, 13]:
            menu_items[current_row]["func"](stdscr, user)
            return
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1

        print_menu(stdscr, current_row)

def logout(stdscr, user):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    goodby_message = f"Take care {user.username}, see YOU around! ..."

    stdscr.addstr(h // 2, w // 2 - 20, "Are you sure you want to leave?")
    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press 'y' to leave, 'n' to continue.")
    stdscr.refresh()
    confirm_key = stdscr.getch()
    if confirm_key == ord('n'):
        load_dashboard(stdscr, user)
    elif confirm_key == ord('y'):
        stdscr.clear()
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(h // 2 - 5, w // 2 - len(goodby_message) // 2, goodby_message)
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        time.sleep(3)
        exit_program(stdscr)

def show_menu(stdscr, user=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    total_price = 0
    selected_items = {}

    def handle_err(error: str):
        stdscr.clear()
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(h // 2 + 2, w // 2 - len(error) // 2, error)
        stdscr.attroff(curses.color_pair(3))
        menu_items = [
            {"label": "Try Again", "func": show_menu},
            {"label": "Back to dashboard", "func": load_dashboard}
        ]
        current_row = 0

        def print_menu(stdscr, current_row):
            h, w = stdscr.getmaxyx()
            for idx, item in enumerate(menu_items):
                x = w // 2 - len(item["label"]) // 2
                y = h // 2 - len(menu_items) // 2 + idx + 6
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, item["label"])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, item["label"])
            stdscr.refresh()

        print_menu(stdscr, current_row)

        while True:
            key = stdscr.getch()
            if key in [10, 13]:
                menu_items[current_row]["func"](stdscr, user)
                return
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1

            print_menu(stdscr, current_row)

    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM food_menu"
        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            menu = [{"category": "Foods", "items": []}, {"category": "Drinks", "items": []}]
            for row in result:
                item = {"title": row[1], "price": row[2], "category": row[3]}
                if item["category"] == "Foods":
                    menu[0]["items"].append(item)
                else:
                    menu[1]["items"].append(item)
            cursor.close()
            close_connection(connection)
    else:
        stdscr.addstr(h // 2 + 2, w // 2 - 10, err)
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0
    total_items = sum(len(category['items']) for category in menu)

    def print_menu(stdscr, current_row):
        stdscr.clear()
        y = h // 2 - total_items // 2 - len(menu)



        for category in menu:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, w // 2 - len(category['category']) // 2, category['category'])
            stdscr.attroff(curses.color_pair(1))
            y += 1
            for item in category['items']:
                x = w // 2 - len(f"{item['title']} - ${item['price']}") // 2
                if menu.index(category) == current_row // len(menu[0]['items']):
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, f"{item['title']} - ${item['price']}")
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, f"{item['title']} - ${item['price']}")
                y += 1
        stdscr.refresh()

    print_menu(stdscr, current_row)
    
    while True:
        key = stdscr.getch()
        if key in [10, 13]:
            category_idx = current_row // len(menu[0]['items'])
            item_idx = current_row % len(menu[category_idx]['items'])
            selected_item = menu[category_idx]['items'][item_idx]
            title = selected_item['title']
            price = selected_item['price']

            if title in selected_items:
                selected_items[title] += 1
            else:
                selected_items[title] = 1
            total_price += price

            stdscr.clear()
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(h // 2, w // 2 - 20, "Added {} to your order.".format(title))
            stdscr.attroff(curses.color_pair(2))
            stdscr.addstr(h // 2 + 1, w // 2 - 20, "Press 'q' to checkout, or 'c' to continue.")
            stdscr.refresh()
            next_action = stdscr.getch()
            if next_action == ord('q'):
                break
            else:
                print_menu(stdscr, current_row)
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < total_items - 1:
            current_row += 1

        print_menu(stdscr, current_row)
    
    if total_price > 0:
        stdscr.clear()
        stdscr.addstr(h // 2, w // 2 - 10, "Your order:")
        y = h // 2 + 1
        for item, qty in selected_items.items():
            stdscr.addstr(y, w // 2 - 10, "{} x{}".format(item, qty))
            y += 1
        stdscr.addstr(y, w // 2 - 10, "Total: ${}".format(total_price))
        stdscr.refresh()
        stdscr.getch()
    if user:
        load_dashboard(stdscr, user)
    else:
        start_menu(stdscr)

def show_users(stdscr, user):
    pass

def login(stdscr):
    curses.curs_set(1)
    stdscr.keypad(True)
    
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter your credentials")
    stdscr.addstr(2, 0, "Username: ")
    curses.echo()
    username = stdscr.getstr(2, 10, 20).decode('utf-8')
    stdscr.addstr(3, 0, "Password: ")
    password = stdscr.getstr(3, 10, 20).decode('utf-8')
    stdscr.clear()

    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        cursor.close()
        close_connection(connection)

        if result:
            logged_user = User(*result)
            stdscr.addstr(5, 5, "Login successful. Welcome!")
            stdscr.refresh()
            time.sleep(2)
            load_dashboard(stdscr, logged_user)
        else:
            stdscr.addstr(5, 5, "Invalid credentials. Try again.")
            stdscr.refresh()
            time.sleep(2)
            login(stdscr)
    else:
        stdscr.addstr(5, 5, err)
        stdscr.refresh()
        stdscr.getch()

def register(stdscr):
    curses.curs_set(1)
    stdscr.keypad(True)
    
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter your details")
    stdscr.addstr(2, 0, "Username: ")
    curses.echo()
    username = stdscr.getstr(2, 10, 20).decode('utf-8')
    stdscr.addstr(3, 0, "Password: ")
    password = stdscr.getstr(3, 10, 20).decode('utf-8')
    stdscr.addstr(4, 0, "Confirm Password: ")
    confirm_password = stdscr.getstr(4, 17, 20).decode('utf-8')
    stdscr.clear()

    if password == confirm_password:
        connection, err = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                stdscr.addstr(5, 5, "Username already exists. Try again.")
                stdscr.refresh()
                time.sleep(2)
                register(stdscr)
            else:
                query = "INSERT INTO users (username, password, isAdmin) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, password, False))
                connection.commit()
                cursor.close()
                close_connection(connection)
                stdscr.addstr(5, 5, "Registration successful. Please login.")
                stdscr.refresh()
                time.sleep(2)
                login(stdscr)
        else:
            stdscr.addstr(5, 5, err)
            stdscr.refresh()
            stdscr.getch()
    else:
        stdscr.addstr(5, 5, "Passwords do not match. Try again.")
        stdscr.refresh()
        time.sleep(2)
        register(stdscr)

def exit_program(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Goodbye!")
    stdscr.refresh()
    time.sleep(1)
    return

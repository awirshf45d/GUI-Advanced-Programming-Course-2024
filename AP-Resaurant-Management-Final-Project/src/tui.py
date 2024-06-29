import curses
import curses.ascii
import time
from db.models import User,FoodItemOnMenu
from db.db import close_connection, connect_to_database



def launch():
    curses.wrapper(start_menu)


def start_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    
    menu_items = [{"label":"Login","func":"login"},
                  {"label":"Register","func":"register"},
                   {"label":"View Menu","func":"show_menu"},
                    {"label":"Exit","func":""}]
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
        # stdscr.addstr(0,0,str(value for idx,value in menu_items.items()), 1)
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    print_menu(stdscr, current_row)
    
    while True:
        key = stdscr.getch()

        if key in [10, 13]:
            if current_row == len(menu_items)-1:
                stdscr.clear()
                h, w = stdscr.getmaxyx()
                goodby_message="Take care, see YOU around! ..."
                stdscr.attron(curses.color_pair(2)) 
                stdscr.addstr( h // 2 - 5,  w // 2 - len(goodby_message)//2, goodby_message)
                stdscr.attroff(curses.color_pair(2))
                stdscr.refresh()
                time.sleep(3)
                exit(1)
            else:
                eval("{}(stdscr)".format(menu_items[current_row]["func"] ))   
            return
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1

        print_menu(stdscr, current_row)


def load_dashboard(stdscr, user):
    curses.curs_set(0)
    stdscr.keypad(True)

    menu_items = [{"label": "Edit your account information", "func": "edit_acc"},
                  {"label": "Food Menu", "func": "show_menu"},
                  {"label": "Logout and Exit", "func": "logout"}]
    if user.isAdmin:
        menu_items.insert(0, {"label": "Admin Panel", "func": "admin_panel"})

    current_row = 0

    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h//4, w//4, user.username)
        if user.isAdmin:
            stdscr.addstr(h//4, w//4 + len(user.username) + 2, "ADMIN", curses.A_BOLD)

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

    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if key in [10, 13]:
            eval("{}(stdscr, user)".format(menu_items[current_row]["func"]))
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

    # Confirm the logout
    stdscr.addstr(h // 2, w // 2 - 20, "Are you sure you want to leave?")
    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press 'y' to leave, 'n' to continue.")
    stdscr.refresh()
    confirm_key = stdscr.getch()
    if confirm_key == ord('n'):
        load_dashboard(stdscr, user)
        return
    elif confirm_key == ord('y'):
        stdscr.clear()
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(h // 2 - 5, w // 2 - len(goodby_message)//2, goodby_message)
        stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        time.sleep(3)
        exit(1)



def show_menu(stdscr, user=None):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    total_price = 0
    selected_items = {}

    def handle_err(error: str):
        stdscr.clear()
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(h//2 +2 , w//2 - len(error)//2, error)
        stdscr.attroff(curses.color_pair(3))
        menu_items = [{"label": "Try Again", "func": "show_menu"},
                      {"label": "Back to dashboard", "func": "load_dashboard"}]
        current_row = 0

        def print_menu(stdscr, current_row):
            h, w = stdscr.getmaxyx()
            for idx, item in enumerate(menu_items):
                x = w // 2 - (len(item["label"]) // 2) - 1
                y = h // 2 - (len(menu_items) // 2) + idx + 6
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
        stdscr.addstr(h//2 + 2, w//2 - 10, err)
        stdscr.refresh()
        stdscr.getch()
        return

    current_row = 0
    total_items = sum(len(category['items']) for category in menu)

    def print_menu(stdscr, current_row):
        stdscr.clear()
        y = h // 2 - total_items // 2 - len(menu)

        for category in menu:
            stdscr.addstr(y, w // 2 - len(category['category']) // 2, category['category'], curses.A_BOLD)
            y += 2
            for idx, item in enumerate(category['items']):
                x = w // 2 - 30
                item_str = f"{item['title']}: ${item['price']}"

                if user and item['title'] in selected_items:
                    item_str += " ✔"

                if idx + sum(len(c['items']) for c in menu[:menu.index(category)]) == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, item_str)
                    stdscr.attroff(curses.color_pair(1))
                elif user and item['title'] in selected_items:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addstr(y, x, item_str)
                    stdscr.attroff(curses.color_pair(2))
                else:
                    stdscr.addstr(y, x, item_str)

                if user and item['title'] in selected_items:
                    qty_str = f" [{selected_items[item['title']]}]"
                    stdscr.addstr(y, x + len(item_str) + 1, qty_str)

                y += 1

        if user:stdscr.addstr(y + 2, w // 2 - 15, f"Total Price: ${total_price}")
        go_back_str="Press 'd' to go back to the dashboard/Login Page."
        if not user:go_back_str="Press 'd' to go back to the dashboard/Login Page, and 'c' to Exit the Program."

        stdscr.addstr(y + 4, w // 2 - len(go_back_str)//2,go_back_str )
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if key == curses.ascii.ESC:
            if not user:start_menu(stdscr)
            return
        elif key == ord('d'):
            if user:
                if not bool(selected_items):
                    load_dashboard(stdscr, user)
                    return
                else:
                    # Confirm the get back 
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 20, "You have selected some items, Are you sure you want to leave?")
                    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press 'y' to leave, 'n' to continue.")
                    stdscr.refresh()
                    confirm_key = stdscr.getch()
                    if confirm_key == ord('n'):
                        print_menu(stdscr,current_row)
                        continue
                    elif confirm_key == ord('y'):
                        load_dashboard(stdscr, user)
                        return

            else:login(stdscr)
            return
        elif not user and key == ord('c'):
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            goodby_message="Take care, see YOU around! ..."
            stdscr.attron(curses.color_pair(2)) 
            stdscr.addstr( h // 2 - 5,  w // 2 - len(goodby_message)//2, goodby_message)
            stdscr.attroff(curses.color_pair(2))
            stdscr.refresh()
            time.sleep(3)
            exit(1)
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < total_items - 1:
            current_row += 1
        elif user and (key == ord("+") or key==ord('-')):
            selected_item = None
            item_index = current_row
            for category in menu:
                if item_index < len(category['items']):
                    selected_item = category['items'][item_index]
                    break
                item_index -= len(category['items'])

            if selected_item:
                title = selected_item['title']
                price = selected_item['price']
                if title in selected_items:
                    if key == ord('+'):
                        selected_items[title] += 1
                        total_price += price
                    elif key == ord('-') and selected_items[title] > 0:
                        selected_items[title] -= 1
                        if selected_items[title] == 0:
                            del selected_items[title]
                        total_price -= price
                elif key == ord('+'):
                    selected_items[title] = 1
                    total_price += price

        print_menu(stdscr, current_row)

def login(stdscr):
    
    def handle_err(error:str):
        stdscr.attron(curses.color_pair(3)) 
        stdscr.addstr(h//2 +2 , w//2 - len(error)//2, error)
        stdscr.attroff(curses.color_pair(3))
        menu_items = [{"label":"Try Again","func":"login"},
                {"label":"Register","func":"register"}]
        current_row = 0

        def print_menu(stdscr, current_row):
            h, w = stdscr.getmaxyx()
            for idx, item in enumerate(menu_items):
                x = w // 2 - (len(item["label"]) // 2) -1
                y = h // 2 - (len(menu_items) // 2) + idx  + 6
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
                eval("{}(stdscr)".format(menu_items[current_row]["func"] ))   
                return
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1

            print_menu(stdscr, current_row)

    
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 8, w//2 - len("Login Page")//2   , "Login Page", curses.A_BOLD | 1)
    stdscr.addstr(h//2 - 2, w//2 - 10, "Username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2 + 1).decode('utf-8')
    if username == "" or " " in username:
        handle_err("Invalid Username, it cant be empty or contains spaces.")
        return

    stdscr.addstr(h//2 - 1, w//2 - 10, "Password: ")
    password = stdscr.getstr(h//2 - 1, w//2 + 1).decode('utf-8')
    if password == "" or " " in password:
        handle_err("Invalid Password, it cant be empty contains spaces.")
        return
    curses.noecho()

    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            stdscr.addstr(h//2, w//2 - 10, f"Welcome back, {username}!")
            time.sleep(2)
            user = User(ID=result[0],username=result[1], password=result[2],isAdmin=result[3],
            location_lat=result[4],location_long=result[5])
            
            cursor.close()
            close_connection(connection)
            load_dashboard(stdscr,user)
            return
        else:
            handle_err("Invalid username or password.")


        cursor.close()
        close_connection(connection)
    else:
        stdscr.addstr(h//2 + 2, w//2 - 10, err)

    stdscr.refresh()

def register(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 2, w//2 - 15, "Choose a username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2 + 4).decode('utf-8')

    def handle_err(error:str):
        stdscr.attron(curses.color_pair(3)) 
        stdscr.addstr(h//2 + 2, w//2 - len(error)//2, error)
        stdscr.attroff(curses.color_pair(3))
        menu_items = [{"label":"Login","func":"login"},
                {"label":"Try Again","func":"register"}]
        current_row = 0

        def print_menu(stdscr, current_row):
            h, w = stdscr.getmaxyx()
            for idx, item in enumerate(menu_items):
                x = w // 2 - (len(item["label"]) // 2) -1
                y = h // 2 - (len(menu_items) // 2) + idx  + 6
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, item["label"])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, item["label"])
            # stdscr.addstr(0,0,str(value for idx,value in menu_items.items()), 1)
            stdscr.refresh()

        print_menu(stdscr, current_row)
        
        while True:
            key = stdscr.getch()

            if key in [10, 13]:
                eval("{}(stdscr)".format(menu_items[current_row]["func"] ))   
                return
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1

            print_menu(stdscr, current_row)

    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            handle_err("Username already exists.")
        elif username == "":
            handle_err("Invalid Username, it cant be empty.")
            return
        else:
            stdscr.addstr(h//2 - 1, w//2 - 15, "Choose a password: ")
            password = stdscr.getstr(h//2 - 1, w//2 + 4).decode('utf-8')
            if password == "":
                handle_err("Invalid Password, it cant be empty.")
                return
            curses.noecho()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            connection.commit()

            stdscr.addstr(h//2, w//2 - 15, f"User {username} registered successfully!")
            time.sleep(2)
            user = User(username=username, password=password)
            
            cursor.close()
            close_connection(connection)
            load_dashboard(stdscr,user)
            return


        cursor.close()
        close_connection(connection)
    else:
        stdscr.addstr(h//2 + 2, w//2 - 10, err)

    stdscr.refresh()
    stdscr.getch()



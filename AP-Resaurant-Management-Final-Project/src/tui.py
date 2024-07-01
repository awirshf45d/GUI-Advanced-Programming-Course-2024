import curses
import curses.ascii
import time
from db.models import User,FoodItemOnMenu
from src.auth import login, register
from src.food_menu import show_menu
from src.order import finalizing_order

def launch():
    curses.wrapper(restaurant_app)

def restaurant_app(stdscr):
    # initializing TUI
    
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.keypad(True)

    user_states = {
        0:"Start_Page",
        1:"Login",
        2:"Register",
        3:"View_Food_Menu",
        4:"dashboard",
        5: "panel",
        6:"order",
        7 : "admin_panel_edit_foodItems",
        8 : "admin_panel_extract_restaurant_order_records",
        9 : "admin_panel_edit_tables",
        40:"Exit"
    }
    user_state, prev_user_state, user, menu_items, current_row, selected_items,total_price = None, None, None, None, None, None, None
    def reset_state_to_start_page():
        nonlocal user_state,user, prev_user_state, menu_items, current_row
        user_state = 0
        prev_user_state = 0
        user = None
        menu_items = {
            1: "Login",
            2: "Register",
            3: "View Menu",
        40: "Exit"
        }
        current_row = 1

    def reset_state_to_dashboard(user, prev_state):
        nonlocal user_state, prev_user_state, menu_items, current_row, total_price, selected_items
        selected_items = {}
        total_price = 0               
        user_state = 4
        prev_user_state = prev_state
        current_row = 3
        menu_items = {
            3: "Food Menu",
            5: "Panel",
            40: "Logout and Exit"
        }
        if user.isAdmin:
            menu_items[5]= "Admin Panel"
    def reset_state_to_login_page():
        nonlocal user_state, prev_user_state, menu_items, current_row                        
        user_state = 1
        current_row = 1
        prev_user_state = 1
        menu_items = {}

    def reset_state_to_finalizing_order():
        nonlocal user_state, current_row, prev_user_state, menu_items
        prev_user_state, user_state = 3, 6 # food menu , order
        current_row = 1
        menu_items = {}
    def reset_state_to_food_menu():
        nonlocal user_state, current_row, prev_user_state, menu_items
        prev_user_state, user_state = user_state, 3 # 3 -> food menu.
        # food menu functions has running in other env(file/function)        

    def prev_next_keys(key):
        keys = list(menu_items.keys())
        index = keys.index(key)
        return (keys[index - 1] if index > 0 else key, keys[index + 1] if index < len(keys) - 1 else key)   
        
    def reset_state_to_pannel(user):#  panel 5
        nonlocal user_state, current_row, prev_user_state, menu_items
        user_state = 5
        prev_user_state = 4 # dashboard
        current_row = 3
        menu_items = {
            3: "Previous Orders",
            4 : "Back to Dashboard"      
        }
        if user.isAdmin:
            menu_items[7]= "Edit Food Menu"
            menu_items[8]= "See Restaurant Order Records"
            menu_items[9]= "Edit(add/remove) Tables"


    def print_menu(stdscr, current_row):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        y = h // 2 - len(menu_items) // 2
        for state, item in menu_items.items():
            x = w // 2 - len(item) // 2
            y += 1
            if state == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)
        stdscr.refresh()
    reset_state_to_start_page()
    

    while True:
        # keys panel
        key = None
        if (user_state not in (1,2,6,3)): # login , register, order, view menu
            print_menu(stdscr, current_row)
            key = stdscr.getch()
        if key == curses.KEY_UP:
            current_row = prev_next_keys(current_row)[0]
            continue
        elif key == curses.KEY_DOWN:
            current_row = prev_next_keys(current_row)[1]
            continue        
        elif key in (10,13):
            prev_user_state = user_state
            user_state = current_row
        elif key == curses.ascii.ESC:
            user_state, prev_user_state = prev_user_state, user_state
        
        # load correct menu related to the user's state
        if user_state == 0: # start page
            reset_state_to_start_page()
        elif user_state == 1: # login process
            hasSucceed, msg, user = login(stdscr)
            h, w = stdscr.getmaxyx()
            c = 3 if hasSucceed is False else 2
            stdscr.clear()
            stdscr.attron(curses.color_pair(c)) 
            stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
            stdscr.attroff(curses.color_pair(c))
            stdscr.refresh()
            time.sleep(2)
            if hasSucceed == False:
                reset_state_to_start_page()
            elif hasSucceed == True:
                reset_state_to_dashboard(user, prev_state=prev_user_state)
        elif user_state == 2: # register
            hasSucceed, msg, user = register(stdscr)
            
            h, w = stdscr.getmaxyx()
            c = 3 if hasSucceed is False else 2
            stdscr.clear()
            stdscr.attron(curses.color_pair(c)) 
            stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
            stdscr.attroff(curses.color_pair(c))
            stdscr.refresh()
            time.sleep(2)
            if hasSucceed == False:
                reset_state_to_start_page()
            elif hasSucceed == True:
                reset_state_to_login_page()
        elif user_state == 3: # view food menu state
            hasSucceed, msg, next_user_state, selected_items, total_price = show_menu(stdscr=stdscr, total_price_p=total_price, selected_items_p=selected_items, user=user)
            if hasSucceed ==  False:
                    h, w = stdscr.getmaxyx()
                    msg1 = "Redirecting to the Dashboard/Start Page ..."
                    stdscr.clear()
                    stdscr.attron(curses.color_pair(3)) 
                    stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
                    stdscr.attroff(curses.color_pair(3))
                   
                    stdscr.attron(curses.color_pair(2)) 
                    stdscr.addstr(h//2 + 1 , w//2 - len(msg1)//2, msg1)
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.refresh()
                    time.sleep(2)

                    if user:reset_state_to_dashboard(user,prev_state=user_state)
                    else: reset_state_to_start_page()
                    continue
            else:
                stdscr.clear()
                stdscr.attron(curses.color_pair(2)) 
                stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
                stdscr.attroff(curses.color_pair(2))
                stdscr.refresh()
                time.sleep(2)
                reset_state_to_finalizing_order()
                continue
        elif user_state == 4: # dashboard
            continue 
        elif user_state == 5: # panel
            reset_state_to_pannel(user)
            continue
        elif user_state == 6 : # order
            hasSucceed, msg = finalizing_order(stdscr,user, selected_items, total_price)
            c = 2 if hasSucceed else 3
            stdscr.clear()
            stdscr.attron(curses.color_pair(c)) 
            stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
            stdscr.attroff(curses.color_pair(c))
            stdscr.refresh()
            time.sleep(5)
            if not hasSucceed:
                reset_state_to_food_menu()
            else:
                reset_state_to_dashboard(user, prev_state=prev_user_state)
        elif user_state == 7:
            pass
        elif user_state == 8:
            pass
        elif user_state == 9:
            pass
        elif user_state == 40: # exit
            def exit_program(stdscr, user):
                h, w = stdscr.getmaxyx()
                goodby_message="Take care, see YOU around! ..." if not user else "Take care {}, see YOU around! ...".format(user.username)
                stdscr.attron(curses.color_pair(2)) 
                stdscr.addstr( h // 2 - 5,  w // 2 - len(goodby_message)//2, goodby_message)
                stdscr.attroff(curses.color_pair(2))
                stdscr.refresh()
                time.sleep(3)
                exit(1)
            exit_program(stdscr, user)


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






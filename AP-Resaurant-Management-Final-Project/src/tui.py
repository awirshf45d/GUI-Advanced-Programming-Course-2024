import curses
import curses.ascii
import time
from typing import Optional, Union
from db.models import User
from src.auth import login, register
from src.food_menu import show_menu
from src.order import finalizing_order
from src.panel import load_prev_orders, edit_tables, edit_food_menu, extract_restaurant_order_records

def launch():
    curses.wrapper(restaurant_app)

def restaurant_app(stdscr):
    """
    All User's States:
    0 ➡️ Start page: The initial page where the user begins interacting with the system.
    1 ➡️ "Login":
    2 ➡️ "Register":
    3 ➡️ "View_Food_Menu": The state where the user can browse the available food menu. (two modes -> 1. read only 2. order)
    4 ➡️ "Dashboard": The state where the user can access an overview of their account.
    5 ➡️ "Panel": A state that refer to a control panel.
    6 ➡️ "Order": The state where the user can place an order for food or services.
    7 ➡️ "User_Prev_Orders": The state where the user can view their previous orders.
    8 ➡️ "Admin_Panel_Edit_FoodItems": The state for administrators to edit food items in the system.
    9 ➡️ "Admin_Panel_Extract_Restaurant_Order_Records": The state for administrators to extract restaurant order records.
    10 ➡️ "Admin_Panel_Edit_Tables": The state for administrators to edit tables or seating arrangements.
    40 ➡️ "Exit": The state where the user can exit or log out of the system.
    """



    # initializing TUI
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # text, background -> black, white -> Highlight/Active
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # text, background -> green, black -> success
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK) # text, background -> red, black -> Error
    stdscr.keypad(True)


    user_state : int =  0
    prev_user_state : int = 0
    current_row : int = 0
    user : Union[User, None] = None
    menu_items: dict = {}
    selected_items : dict = {}
    total_price : int = 0
    
    def reset_state_to(target_state: int, prev_state: Optional[int] =None, user: Optional[User]=None) -> None:
        nonlocal user_state, prev_user_state, menu_items, current_row, total_price, selected_items
        current_row = 1
        menu_items = {}
        if target_state == 4 and user: # dashboard
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
        elif target_state == 1: # login page
            user_state = 1
            prev_user_state = 1
        elif target_state == 3 and user: # food menu
            prev_user_state, user_state = user_state, 3
        elif target_state == 6: # finalizing order
            prev_user_state, user_state = 3, 6 # food menu , order
        elif target_state == 0: # start page
            user_state = prev_user_state = 0
            user = None
            menu_items = {
                1: "Login",
                2: "Register",
                3: "View Menu",
            40: "Exit"
            }
            current_row = 1
        elif target_state == 5 and user: # panel
            user_state = 5 
            prev_user_state = 4 # dashboard
            current_row = 7
            menu_items = {
                7: "Previous Orders"
            }
            if user.isAdmin:
                menu_items[8]= "Edit Food Menu"
                menu_items[9]= "See Restaurant Order Records"
                menu_items[10]= "Add/Remove Tables"


    def prev_next_keys(key: int) -> None:
        keys = list(menu_items.keys())
        index = keys.index(key)
        return (keys[index - 1] if index > 0 else key, keys[index + 1] if index < len(keys) - 1 else key)   
        

    def print_menu(stdscr, current_row : int, menu_items : dict) -> None:
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
    
    def print_hasSucced_message(stdscr, hasSucceed : bool, msg: str, success_state : int, failure_state:int, prev_state : Optional[int] = None, user : Optional[User] = None , time_to_sleep: int = 3, second_msg: Optional[str] = None) -> None:
        h, w = stdscr.getmaxyx()
        c = 3 if hasSucceed is False else 2
        stdscr.clear()
        stdscr.attron(curses.color_pair(c)) 
        stdscr.addstr(h//2 , w//2 - len(msg)//2, msg)
        stdscr.attroff(curses.color_pair(c))

        if second_msg:
            stdscr.attron(curses.color_pair(2)) 
            stdscr.addstr(h//2 + 1 , w//2 - len(second_msg)//2, second_msg)
            stdscr.attroff(curses.color_pair(2))
        
        stdscr.refresh()


        time.sleep(time_to_sleep)

        reset_state_to(success_state if hasSucceed else failure_state, prev_state, user)

    reset_state_to(0)



    while True:
        # keyboard
        key = None
        if (user_state not in (1,2,6,3)): # login , register, order, view menu
            print_menu(stdscr, current_row, menu_items)
            key = stdscr.getch()
        if key == curses.KEY_UP:
            current_row = prev_next_keys(current_row)[0] # before 
            continue
        elif key == curses.KEY_DOWN:
            current_row = prev_next_keys(current_row)[1] # after
            continue        
        elif key in (10,13): # enter, line-feed
            prev_user_state = user_state
            user_state = current_row
        elif key == curses.ascii.ESC: # Esc -> swap the previous and current states
            user_state, prev_user_state = prev_user_state, user_state
        
        # load the page based on the user's state
        if user_state == 0: # start page
            reset_state_to(0)
        elif user_state == 1: # login process
            hasSucceed, msg, user = login(stdscr)
            print_hasSucced_message(stdscr, hasSucceed, msg, success_state=4, failure_state=0, prev_state=prev_user_state, user=user ) # dashboard 4, start page 0
        elif user_state == 2: # register
            hasSucceed, msg, user = register(stdscr)
            print_hasSucced_message(stdscr, hasSucceed, msg, success_state=1, failure_state=0, prev_state=prev_user_state, user=user )
        elif user_state == 3: # view food menu state
            hasSucceed, msg, selected_items, total_price = show_menu(stdscr=stdscr, total_price_p=total_price, selected_items_p=selected_items, user=user)
            print_hasSucced_message(stdscr, hasSucceed , msg, success_state=6, failure_state= 4 if user else 0, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard/Start Page ...") # s-state -> order, f-state -> dashboard, start page
            continue
        elif user_state == 4: # dashboard
            reset_state_to(4, prev_user_state, user)
            continue 
        elif user_state == 5: # panel
            reset_state_to(5, prev_user_state, user)
            continue
        elif user_state == 7: # load previous orders
            hasSucceed, msg = load_prev_orders(stdscr, user)
            print_hasSucced_message(stdscr,hasSucceed, msg, success_state=4, failure_state= 4, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard ...") # s-state -> dashboard, f-state -> dashboard
            continue
        elif user_state == 8 :  # 8 edit food menu
            hasSucceed, msg = edit_food_menu(stdscr)
            print_hasSucced_message(stdscr,hasSucceed, msg, success_state=4, failure_state= 4, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard ...") # s-state -> dashboard, f-state -> dashboard
            continue
        elif user_state == 9 : # 9 extract all restaurant records
            hasSucceed, msg = extract_restaurant_order_records(stdscr)
            print_hasSucced_message(stdscr,hasSucceed, msg, success_state=4, failure_state= 4, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard ...") # s-state -> dashboard, f-state -> dashboard
            continue
        elif user_state == 10: # 10 add/remove tables
            hasSucceed, msg = edit_tables(stdscr)
            print_hasSucced_message(stdscr,hasSucceed, msg, success_state=4, failure_state= 4, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard ...") # s-state -> dashboard, f-state -> dashboard
            continue
        elif user_state == 6 : # order
            hasSucceed, msg = finalizing_order(stdscr,user, selected_items, total_price)
            print_hasSucced_message(stdscr,hasSucceed, msg, success_state=4, failure_state= 3, prev_state=prev_user_state, user=user, second_msg="Redirecting to the Dashboard ...") # s-state -> dashboard, f-state -> view food menu
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






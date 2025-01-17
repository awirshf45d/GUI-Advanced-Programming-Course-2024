from db.db import close_connection, connect_to_database
from db.models import User
import curses
from time import sleep
from typing import Tuple, Union, Optional
from datetime import datetime
def load_prev_orders(stdscr, user:User) -> Tuple[bool, str]:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT order_id, order_date, item_title, quantity, latitude, longitude FROM restaurant_orders WHERE user_id = %s"
        cursor.execute(query, (user.id,))
        result = cursor.fetchall()

        if result:
            stdscr.addstr(0, 0, "Previous Orders:")
            for idx, order in enumerate(result):
                order_id, order_date, item_title, quantity, latitude, longitude = order
                one_row = f"Order ID: {order_id}, Date: {order_date}, Item: {item_title}, Quantity: {quantity}, Lat: {latitude}, Lon: {longitude}"
                stdscr.addstr(h//2 - 5 + idx + 1, w//2 - len(one_row)//2, one_row)

            stdscr.refresh()
        else:
            stdscr.addstr(h//2, w//2, "No previous orders found.")
            stdscr.refresh()
        
        stdscr.addstr(h-2, w//2 - len("Press any key to return to the dashboard page.")//2, "Press any key to return to the dashboard page.")
        stdscr.refresh()
        stdscr.getch()
        
        cursor.close()
        close_connection(connection)
        return True, ""
    else:
        return False, "Something Went Wrong while fetching previous orders from DB: {}".format(err)



def edit_tables(stdscr) -> Tuple[bool, str]:
    edit_type = None
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Tables...") // 2, "Edit Tables...", curses.A_BOLD)
        
        q = "Select the type of edit you would like to make: (a) Make a table available, or (b) Add a new table."
        stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
        curses.echo()
        edit_type = chr(stdscr.getch())
        if edit_type not in ("a", "b"):
            stdscr.addstr(h // 2, w // 2 - len("Invalid Inputs") // 2, "Invalid Inputs")
            stdscr.refresh()
            sleep(1.5)
            continue
        else:
            break

    if edit_type == "a":
        connection, err = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "SELECT id FROM tables WHERE is_available = 0"
            cursor.execute(query)
            result = cursor.fetchall()
            reserved_tables = ', '.join(str(row[0]) for row in result)
            
            user_selected_table = None

            if not reserved_tables:
                stdscr.clear()
                stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Tables...") // 2, "Edit Tables...", curses.A_BOLD)
                q = "All Tables are available..."
                stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
                stdscr.refresh()
                sleep(1)
            else:
                while True:
                    stdscr.clear()
                    stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Tables...") // 2, "Edit Tables...", curses.A_BOLD)

                    q = f"Which table do you want to make available? Busy Tables: {reserved_tables}"
                    stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
                    curses.echo()
                    
                    user_selected_table = stdscr.getstr(h // 2 - 4, w // 2 - len(q) // 2 + len(q)).decode('utf-8')
                    if user_selected_table == "n":
                        break
                    elif user_selected_table not in reserved_tables.split(", "):
                        stdscr.addstr(h // 2 + 6, w // 2 - len("Invalid choice, Try again ...") // 2, "Invalid choice, Try again ...")
                        stdscr.refresh()
                        sleep(1.5)
                        continue
                    else:
                        break
            
            if user_selected_table != "n" and reserved_tables:
                update_query = "UPDATE tables SET is_available = 1, reserved_by_user = NULL WHERE id = %s"
                cursor.execute(update_query, (user_selected_table,))
                connection.commit()
                cursor.close()
                close_connection(connection)
                return True, "Table availability updated."
            
            cursor.close()
            close_connection(connection)
        else:
            return False, "Something went wrong while establishing connection with DB: {}".format(err)

    
    elif edit_type == "b":
        connection, err = connect_to_database()
        if connection:
            cursor = connection.cursor()
            new_table_count = None
            while True:
                stdscr.clear()
                stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Tables...") // 2, "Edit Tables...", curses.A_BOLD)
                q = "Enter the Number of tables which you want to add:"
                stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
                curses.echo()
                new_table_count = stdscr.getstr(h // 2 - 4, w // 2 - len(q) // 2 + len(q)).decode('utf-8')
                if new_table_count.isdigit() and int(new_table_count)>0:
                    break
                else:
                    stdscr.addstr(h // 2, w // 2 - len("Invalid Inputs") // 2, "Invalid Inputs")
                    stdscr.refresh()
                    sleep(1.5)
                    continue
            
            for _ in range(int(new_table_count)):
                insert_query = "INSERT INTO tables (is_available) VALUES (1)"
                cursor.execute(insert_query)
            connection.commit()

            
            cursor.close()
            close_connection(connection)
            return True, "New Tables have been added"
        else:
            return False, "Something went wrong while establishing connection with DB: {}".format(err)

def edit_food_menu(stdscr) -> Tuple[bool, str]:
    edit_type = None
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
        
        q = "Select the type of edit you would like to make: (a) Add new items to menu, or (b) Remove items from the menu."
        stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
        curses.echo()
        edit_type = chr(stdscr.getch())
        if edit_type not in ("a", "b"):
            stdscr.addstr(h // 2, w // 2 - len("Invalid Inputs") // 2, "Invalid Inputs")
            stdscr.refresh()
            sleep(1.5)
            continue
        else:
            break

    connection, err = connect_to_database()
    if not connection:
        return False, "Something went wrong while establishing connection with DB: {}".format(err)
    
    cursor = connection.cursor()

    stdscr.clear()
    stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
    cursor.execute("SELECT id, title, price, category FROM food_menu")
    menu_items = cursor.fetchall()
    menu_display = "Current Menu:\n"
    for item in menu_items:
        menu_display += f"{item[0]}. {item[1]} - ${item[2]:.2f} [{item[3]}]\n"
    stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)

    if edit_type == "a":
        # Add new items to menu
        new_item_title = None
        new_item_price = None
        new_item_category = None
        
        while True:
            stdscr.clear()
            stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
            stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)
            
            stdscr.addstr(h // 2 - 4, w // 2 - len("Enter the item title to add: ") // 2, "Enter the item title to add: ")
            new_item_title = stdscr.getstr(h // 2 - 4, w // 2 + len("Enter the item title to add: ") // 2).decode('utf-8')
            
            if new_item_title:
                break
            else:
                stdscr.addstr(h // 2, w // 2 - len("Invalid input, try again.") // 2, "Invalid input, try again.")
                stdscr.refresh()
                sleep(1.5)
        
        while True:
            stdscr.clear()
            stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
            stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)
            
            stdscr.addstr(h // 2, w // 2 - len("Enter the price: ") // 2, "Enter the price: ")
            new_item_price = stdscr.getstr(h // 2, w // 2 + len("Enter the price: ") //2).decode('utf-8')
            
            if new_item_price:
                try:
                    new_item_price = float(new_item_price)
                    if new_item_price > 0:
                        break            
                except:
                    pass
            stdscr.addstr(h // 2 + 2, w // 2 - len("Invalid input, try again.") // 2, "Invalid input, try again.")
            stdscr.refresh()
            sleep(1.5)
        
        while True:
            stdscr.clear()
            stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
            stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)
            
            stdscr.addstr(h // 2 + 4, w // 2 - len("Enter the category (drinks, food): ") // 2, "Enter the category (drinks, food): ")
            new_item_category = stdscr.getstr(h // 2 + 4, w // 2 + len("Enter the category (drinks, food): ") // 2).decode('utf-8').lower()
            
            if new_item_category in ("drinks", "food"):
                break
            else:
                stdscr.addstr(h // 2 + 6, w // 2 - len("Invalid input, try again.") // 2, "Invalid input, try again.")
                stdscr.refresh()
                sleep(1.5)
        
        insert_query = "INSERT INTO food_menu (title, price, category) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (new_item_title, new_item_price, new_item_category.capitalize()))
        connection.commit()
        
        return True, "New item added to menu"
    
    elif edit_type == "b":
        # Remove items from menu
        item_id_to_remove = None
        
        while True:
            stdscr.clear()
            stdscr.addstr(h // 2 - 10, w // 2 - len("Edit Food Menu...") // 2, "Edit Food Menu...", curses.A_BOLD)
            stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)
            
            stdscr.addstr(h // 2 - 4, w // 2 - len("Enter the item ID to remove: ") // 2, "Enter the item ID to remove: ")
            item_id_to_remove = stdscr.getstr(h // 2 - 4, w // 2 +len("Enter the item ID to remove: ") // 2 ).decode('utf-8')
        
            if item_id_to_remove.isdigit():
                item_id_to_remove = int(item_id_to_remove)
                if item_id_to_remove in (item[0] for item in menu_items):
                    break
                
            stdscr.addstr(h // 2, w // 2 - len("Invalid input, try again.") // 2, "Invalid input, try again.")
            stdscr.refresh()
            sleep(1.5)
        
        delete_query = "DELETE FROM food_menu WHERE id = %s"
        cursor.execute(delete_query, (item_id_to_remove,))
        connection.commit()
        
        stdscr.addstr(h // 2 + 4, w // 2 - len("Item removed from menu.") // 2, "Item removed from menu.", curses.A_BOLD)
        stdscr.refresh()
        sleep(2)
    
    cursor.close()
    close_connection(connection)
    return True, "Menu update completed successfully."

def extract_restaurant_order_records(stdscr):
    """
    Steps:
    - start messages, and guide
    - filter by (+ validate all inputs)
        - Date (YYYY-MM-DD) or leave it empty (Start Date and End Date)
        - filter by item title (single or multiple)
        - select by order type -> dine-in/takeout or delivery (based on lat and lon in the table)
    - show results and press any key to try again, and press Esc to back to the dashboard
    """
    start_date:str = ""
    end_date:str = ""

    h, w = stdscr.getmaxyx()

    def print_banner(banner: str):
        stdscr.clear()
        stdscr.addstr(h // 2 - 10, w // 2 - len(banner) // 2, banner, curses.A_BOLD)
        stdscr.refresh()

    print_banner("Filter Restaurant Orders by Date...")

    connection, err = connect_to_database()
    if not connection:
        return False, f"Something went wrong while establishing connection with DB: {err}"

    cursor = connection.cursor()

    def validate_supplied_date(date: str) -> Tuple[bool, str]:
        if date.lower() == 'n':
            return True, ""
        else:
            try:
                datetime.strptime(date, '%Y-%m-%d')
                return True, date
            except ValueError:
                return False, date

    def get_date_input(banner: str, prompt:str) -> str:
        while True:
            print_banner(banner)
            stdscr.addstr(h // 2 - 6, w // 2 - len(prompt) // 2, prompt)
            curses.echo()
            date_input = stdscr.getstr(h // 2 - 6, w // 2 + len(prompt) // 2).decode('utf-8')
            
            isValid, date_input = validate_supplied_date(date_input)
            if not isValid:
                stdscr.addstr(h // 2 - 2, w // 2 - len("Invalid date format. Try Again.") // 2, "Invalid date format. Try Again.")
                stdscr.refresh()
                sleep(1.5)
            else:
                return date_input

    sleep(2)
    start_date = get_date_input("Filter Restaurant Orders by Date...", "Enter start date (YYYY-MM-DD) or n: ")
    stdscr.addstr(0,0,f"'{start_date}'")
    end_date = get_date_input("Filter Restaurant Orders by Date...","Enter end date (YYYY-MM-DD) or n: ")

    print_banner("Filter Restaurant Orders by Food Menu Items or Category...")

    cursor.execute("SELECT id, title, price, category FROM food_menu")
    menu_items = cursor.fetchall()
    
    for idx, item in enumerate(menu_items):
        menu_item = f"{item[0]}. {item[1]} - ${item[2]} [{item[3]}]"
        stdscr.addstr(h // 2 - 8 + idx, w // 2 - len(menu_item) // 2, menu_item)
    stdscr.refresh()

    stdscr.addstr(h // 2, w // 2 - len("Enter the item title(s) separated by commas or n: ") // 2, "Enter the item title(s) separated by commas or n: ")
    curses.echo()
    item_titles = stdscr.getstr(h // 2, w // 2 + len("Enter the item title(s) separated by commas or n: ") // 2).decode('utf-8')



    stdscr.addstr(h // 2 + 2, w // 2 - len("Enter the order type (delivery, dine-in/takeout) or n: ") // 2, "Enter the order type (delivery, dine-in/takeout) or n: ")
    curses.echo()
    order_type = stdscr.getstr(h // 2 + 2, w // 2 + len("Enter the order type (delivery, dine-in/takeout) or n: ") // 2).decode('utf-8')

    query = "SELECT * FROM restaurant_orders WHERE 1=1"
    params = []

    if start_date.lower() != 'n':
        query += " AND order_date >= %s"
        params.append(start_date)

    if end_date.lower() != 'n':
        query += " AND order_date <= %s"
        params.append(end_date)

    if item_titles.lower() != 'n':
        item_titles_list = tuple(title.strip() for title in item_titles.split(','))
        placeholders = ', '.join(['%s'] * len(item_titles_list))
        query += f" AND item_title IN ({placeholders})"
        params.extend(item_titles_list)

    if order_type.lower() != 'n':
        if order_type.lower() == 'delivery':
            query += " AND latitude IS NOT NULL AND longitude IS NOT NULL"
        else:  # dine-in/takeout
            query += " AND latitude IS NULL AND longitude IS NULL"

    cursor.execute(query, params)
    orders = cursor.fetchall()

    print_banner("Filtered Orders...")
    
    for idx,order in enumerate(orders):
        order_display = f"Order ID: {order[0]}\tDate: {order[1]}\tItem: {order[2]}\tQuantity: {order[3]}\tUser ID: {order[4]}\tLatitude: {order[5]}\tLongitude: {order[6]}\n"
        stdscr.addstr(h // 2 - 6 + idx, w // 2 - len(order_display) // 2, order_display)

    stdscr.refresh()
    
    stdscr.addstr(h-2, w//2 - len("Press any key to return to the dashboard page.")//2, "Press any key to return to the dashboard page.")
    stdscr.refresh()
    stdscr.getch()
    cursor.close()
    close_connection(connection)
    return True, "Order records filtered successfully."


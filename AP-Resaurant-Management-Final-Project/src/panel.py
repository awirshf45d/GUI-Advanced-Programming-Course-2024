from db.db import close_connection, connect_to_database
from db.models import User
import curses
from time import sleep
from typing import Tuple, Union, Optional
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
                stdscr.addstr(h//2 + idx + 1, w//2 - len(one_row)//2, )

            stdscr.refresh()
        else:
            stdscr.addstr(h//2, w//2, "No previous orders found.")
            stdscr.refresh()
        
        stdscr.addstr(h - 1, 0, "Press any key to return to the dashboard page.")
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
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 2 - 10, w // 2 - len("Filter Restaurant Orders...") // 2, "Filter Restaurant Orders...", curses.A_BOLD)

    connection, err = connect_to_database()
    if not connection:
        return False, "Something went wrong while establishing connection with DB: {}".format(err)
    
    cursor = connection.cursor()
    
    # Show the menu items
    stdscr.clear()
    stdscr.addstr(h // 2 - 10, w // 2 - len("Restaurant Menu...") // 2, "Restaurant Menu...", curses.A_BOLD)
    cursor.execute("SELECT id, title, price, category FROM food_menu")
    menu_items = cursor.fetchall()
    menu_display = "Current Menu:\n"
    for item in menu_items:
        menu_display += f"{item[0]}. {item[1]} - ${item[2]:.2f} [{item[3]}]\n"
    stdscr.addstr(h // 2 - 6, w // 2 - len(menu_display.split('\n')[0]) // 2, menu_display)

    # Get filter inputs from user
    stdscr.addstr(h // 2 - 4, w // 2 - len("Enter start date (YYYY-MM-DD) or N: ") // 2, "Enter start date (YYYY-MM-DD) or N: ")
    start_date = stdscr.getstr(h // 2 - 4, w // 2 + len("Enter start date (YYYY-MM-DD) or N: ") // 2).decode('utf-8')

    stdscr.addstr(h // 2 - 2, w // 2 - len("Enter end date (YYYY-MM-DD) or N: ") // 2, "Enter end date (YYYY-MM-DD) or N: ")
    end_date = stdscr.getstr(h // 2 - 2, w // 2 + len("Enter end date (YYYY-MM-DD) or N: ") // 2).decode('utf-8')

    stdscr.addstr(h // 2, w // 2 - len("Enter the item ID or N: ") // 2, "Enter the item ID or N: ")
    item_id = stdscr.getstr(h // 2, w // 2 + len("Enter the item ID or N: ") // 2).decode('utf-8')

    stdscr.addstr(h // 2 + 2, w // 2 - len("Enter the order type (delivery, dine-in/takeout) or N: ") // 2, "Enter the order type (delivery, dine-in/takeout) or N: ")
    order_type = stdscr.getstr(h // 2 + 2, w // 2 + len("Enter the order type (delivery, dine-in/takeout) or N: ") // 2).decode('utf-8')

    # Construct the query based on non-empty inputs
    query = "SELECT * FROM restaurant_orders WHERE 1=1"
    params = []

    if start_date != 'N':
        query += " AND order_date >= %s"
        params.append(start_date)
    
    if end_date != 'N':
        query += " AND order_date <= %s"
        params.append(end_date)
    
    if item_id != 'N':
        query += " AND item_title = (SELECT title FROM food_menu WHERE id = %s)"
        params.append(item_id)
    
    if order_type != 'N':
        if order_type.lower() == 'delivery':
            query += " AND latitude IS NOT NULL AND longitude IS NOT NULL"
        else:  # dine-in/takeout
            query += " AND latitude IS NULL AND longitude IS NULL"

    cursor.execute(query, params)
    orders = cursor.fetchall()

    # Display the filtered orders
    stdscr.clear()
    stdscr.addstr(h // 2 - 10, w // 2 - len("Filtered Orders...") // 2, "Filtered Orders...", curses.A_BOLD)
    order_display = "Filtered Orders:\n"
    for order in orders:
        order_display += f"Order ID: {order[0]}, Date: {order[1]}, Item: {order[2]}, Quantity: {order[3]}, User ID: {order[4]}, Latitude: {order[5]}, Longitude: {order[6]}\n"
    stdscr.addstr(h // 2 - 6, w // 2 - len(order_display.split('\n')[0]) // 2, order_display)

    stdscr.refresh()
    sleep(5)
    
    cursor.close()
    close_connection(connection)
    return True, "Order records filtered successfully."

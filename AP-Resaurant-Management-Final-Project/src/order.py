import curses
import haversine as hs
from db.db import connect_to_database, close_connection
from datetime import datetime
from time import sleep
def finalizing_order(stdscr, user, selected_items, total_price):
    order_type = None
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 2 - 10, w // 2 - len("Finalizing your order ...") // 2, "Finalizing your order ...", 2)
        
        q = "Select the type of your order (a) Dine-In/Takeout Order (b) Delivery Order"
        stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
        curses.echo()
        order_type = chr(stdscr.getch())
        if order_type not in ("a", "b"):
            stdscr.addstr(h // 2 , w // 2 - len("Invalid Inputs") // 2, "Invalid Inputs")
            stdscr.refresh()
            sleep(1.5)
            continue
        else:
            break


    if order_type == "a":
        connection, err = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "SELECT id FROM tables WHERE is_available = 1"
            cursor.execute(query)
            result = cursor.fetchall()
            available_tables = ', '.join(str(row[0]) for row in result)
            
            user_reserved_table = None

            if not available_tables:
                stdscr.clear()
                stdscr.addstr(h // 2 - 10, w // 2 - len("Finalizing your order ...") // 2, "Finalizing your order ...", curses.A_BOLD | 1)
                q = "All Tables have been reserved by other customers ..."
                stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
                stdscr.refresh()
                sleep(1)
            else:
                while True:
                    stdscr.clear()
                    stdscr.addstr(h // 2 - 10, w // 2 - len("Finalizing your order ...") // 2, "Finalizing your order ...", curses.A_BOLD | 1)
                    q = f"Do you want to reserve any table? Available Tables: {available_tables}"
                    stdscr.addstr(h // 2 - 4, w // 2 - len(q) // 2, q)
                    curses.echo()
                    user_reserved_table = stdscr.getstr(h // 2 - 4, w // 2 - len(q) // 2 + len(q)).decode('utf-8')
                    if user_reserved_table == "n":
                        break
                    elif user_reserved_table not in available_tables.split(", "):
                        stdscr.addstr(h // 2 + 6, w // 2 - len("Invalid choice, Try again ...") // 2, "Invalid choice, Try again ...")
                        stdscr.refresh()
                        sleep(1.5)
                        continue
                    else:
                        break
            close_connection(connection)
            cursor.close()
        else:
            return False, "Something went wrong while establishing connection with DB. {}".format(err)
        
        hasSucceed, msg = insert_orders(selected_items, user.id, None, None)
        if not hasSucceed:
            return hasSucceed, msg
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h//2, w//2 - len(msg)//2, msg, 2)
        stdscr.refresh()
        sleep(2)
        if user_reserved_table != "n" and available_tables:
            hasSucceed, msg = reserve_table(user_reserved_table, user.id)
            if not hasSucceed:
                return hasSucceed, msg
            h, w = stdscr.getmaxyx()
            stdscr.addstr(h//2+1, w//2 - len(msg)//2, msg, 2)
            stdscr.refresh()
            sleep(2)
        return True, "Everything has been completed successfully. Have a wonderful time!"
    else:
        is_ok, msg, (longitude, latitude) = get_destination_loc(stdscr)
        if is_ok:
            hasSucceed, msg = insert_orders(selected_items, user.id, longitude, latitude)
            if not hasSucceed:
                return hasSucceed, msg
            return True, "Everything has been completed successfully. Have a wonderful time! your meal will be there soon ..."
        else:
            return False, "Order could not be completed: {}".format(msg)

def insert_orders(selected_items, user_id, longitude=None, latitude=None):
    connection,err = connect_to_database()
    if not connection:
        return False, "Failed to connect to database"

    cursor = connection.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for item, quantity in selected_items.items():
        query = "INSERT INTO restaurant_orders (order_date, item_title, quantity, user_id, longitude, latitude) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (current_time, item, quantity, user_id, longitude, latitude))
    
    connection.commit()
    cursor.close()
    connection.close()

    return True, "Orders successfully inserted into database"

def reserve_table(table_id, user_id):
    connection,err = connect_to_database()
    if not connection:
        return False, "Failed to connect to database"

    cursor = connection.cursor()
    update_query = "UPDATE tables SET is_available = %s, reserved_by_user = %s WHERE id = %s"
    cursor.execute(update_query, (0, user_id, table_id))
    connection.commit()
    cursor.close()
    connection.close()
    return True, "The reservation for Table ID {} has been successfully made".format(table_id)

def get_destination_loc(stdscr):
    loc_source = (19.0760, 72.8777)  # hard-coded geo-location
    longitude, latitude = None, None

    def get_long_lat(stdscr):
        nonlocal longitude, latitude
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(h // 2 - 8, w // 2 - len("Delivery Order...") // 2, "Delivery Order...", curses.A_BOLD | 1)
            stdscr.addstr(h // 2 - 2, w // 2 - len("Longitude: ") // 2, "Longitude: ")
            curses.echo()
            longitude = stdscr.getstr(h // 2 - 2, w // 2 + len("Longitude: ") // 2 + 1).decode('utf-8')
            try:
                longitude = float(longitude)
                break
            except ValueError:
                stdscr.addstr(h // 2 + 6, w // 2 - len("Invalid Longitude, Try again ...") // 2, "Invalid Longitude, Try again ...")
                stdscr.refresh()
                sleep(2)
                continue
        
        while True:
            stdscr.clear()
            stdscr.addstr(h // 2 - 8, w // 2 - len("Delivery Order...") // 2, "Delivery Order...", curses.A_BOLD | 1)
            stdscr.addstr(h // 2 - 2, w // 2 - len("Latitude: ") // 2, "Latitude: ")
            curses.echo()
            latitude = stdscr.getstr(h // 2 - 2, w // 2 + len("Latitude: ") // 2 + 1).decode('utf-8')
            try:
                latitude = float(latitude)
                break
            except ValueError:
                stdscr.addstr(h // 2 + 6, w // 2 - len("Invalid Latitude, Try again ...") // 2, "Invalid Latitude, Try again ...")
                stdscr.refresh()
                sleep(2)
                continue

    get_long_lat(stdscr)
    
    distance = hs.haversine(loc_source, (longitude, latitude), unit=hs.Unit.KILOMETERS)
    
    if distance <= 5:
        return True, "Congratulations! Your location is right in the heart of the party zone!", (longitude, latitude)
    else:
        return False, "Looks like your location is in the forbidden zone, no help available there, sorry!", (None, None)

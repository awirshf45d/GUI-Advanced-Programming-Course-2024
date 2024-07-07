from db.db import close_connection,connect_to_database
from typing import Union, Optional, Tuple
from db.models import User
import curses
import curses.ascii

def show_menu(stdscr ,selected_items_p : dict, total_price_p : int,  user: Optional[User]=None) -> Tuple[bool, str, dict, int ]:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    total_price : int = total_price_p if total_price_p else 0
    selected_items : dict = selected_items_p if selected_items_p else {}
    search_mode : bool = False
    search_query : str = ""

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
        return False, "Something Went Wrong while fetching food Menu from DB. {}".format(err), selected_items, total_price

    current_row = 0
    total_items = sum(len(category['items']) for category in menu)

    def filter_menu(query):
        filtered_menu = [{"category": "Foods", "items": []}, {"category": "Drinks", "items": []}]
        for category in menu:
            for item in category["items"]:
                if query.lower() in item["title"].lower():
                    if category["category"] == "Foods":
                        filtered_menu[0]["items"].append(item)
                    else:
                        filtered_menu[1]["items"].append(item)
        return filtered_menu

    def print_menu(stdscr, current_row):
        stdscr.clear()
        y = h // 2 - total_items // 2 - len(menu)
        items_to_display = filter_menu(search_query) if search_mode else menu

        for category in items_to_display:
            stdscr.addstr(y, w // 2 - len(category['category']) // 2, category['category'], curses.A_BOLD)
            y += 2
            for idx, item in enumerate(category['items']):
                x = w // 2 - 30
                item_str = f"{item['title']}: ${item['price']}"

                if user and item['title'] in selected_items:
                    item_str += " ✔"

                if idx + sum(len(c['items']) for c in items_to_display[:items_to_display.index(category)]) == current_row:
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

        if user and not search_mode:
            stdscr.addstr(y + 2, w // 2 - 15, f"Total Price: ${total_price}")

        if not search_mode:
            go_back_str = "Press 'Esc' to go back to the dashboard/Start Page. Press '/' to search."
            stdscr.addstr(y + 4, w // 2 - len(go_back_str) // 2, go_back_str)

        if search_mode:
            stdscr.addstr(h - 2, 1, "Search: " + search_query)

        stdscr.refresh()

    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if search_mode:
            if key == curses.ascii.ESC:
                search_mode = False
                search_query = ""
                current_row = 0
            elif key in (10, 13):
                search_mode = False
            elif key == curses.KEY_BACKSPACE:
                search_query = search_query[:-1]
            elif key != ord('/'):
                search_query += chr(key)
            print_menu(stdscr, current_row)
            continue

        if key == curses.ascii.ESC:
            if bool(selected_items):
                # Confirm the get back
                q="You have selected some items, Are you sure you want to leave?"
                a="Press 'y' to leave, 'n' to continue."
                stdscr.clear()
                stdscr.addstr(h // 2, w // 2 - len(q)//2,q )
                stdscr.addstr(h // 2 + 1, w // 2 - len(a)//2,a )
                stdscr.refresh()    
                confirm_key = stdscr.getch()
                if confirm_key == ord('n'):
                    print_menu(stdscr, current_row)
                    continue
                elif confirm_key == ord('y'):
                    return False, "", {}, 0
            else:
                return False, "", selected_items, total_price
        elif key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < total_items - 1:
            current_row += 1
        elif user and (key == ord("+") or key == ord('-')):
            selected_item = None
            item_index = current_row
            items_to_display = filter_menu(search_query) if search_mode else menu
            for category in items_to_display:
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
        elif key == ord('/'):
            search_mode = True
        elif key in (10,13):
            if not user:return False, "You haven't login yet ...", {}, 0

            # user has login in the app.
            return True, "Finalizing The Order...", selected_items, total_price
            
                       

        print_menu(stdscr, current_row)

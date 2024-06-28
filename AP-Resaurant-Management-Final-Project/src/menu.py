import curses
import curses.ascii
import json

def show_menu(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    selected_items = {}  # Dictionary to store selected items and their quantities
    total_price = 0  # Variable to store total price of selected items

    try:
        with open('data/menu.json') as f:
            menu = json.load(f)
        
        current_row = 0
        total_items = sum(len(category['items']) for category in menu)

        def print_menu(stdscr, current_row):
            nonlocal total_price
            
            stdscr.clear()
            y = h // 2 - total_items // 2 - len(menu)
            
            for category in menu:
                stdscr.addstr(y, w // 2 - len(category['category']) // 2, category['category'], curses.A_BOLD)
                y += 2
                for idx, item in enumerate(category['items']):
                    x = w // 2 - 30
                    item_str = f"{item['title']}: ${item['price']}"
                    
                    # Add tick mark if item is selected
                    if item['title'] in selected_items:
                        item_str += " ✔"
                    
                    # Highlight selected items in a different color
                    if idx + sum(len(c['items']) for c in menu[:menu.index(category)]) == current_row:
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(y, x, item_str)
                        stdscr.attroff(curses.color_pair(1))
                    elif item['title'] in selected_items:
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(y, x, item_str)
                        stdscr.attroff(curses.color_pair(2))
                    else:
                        stdscr.addstr(y, x, item_str)
                    
                    # Display quantity if item is selected
                    if item['title'] in selected_items:
                        qty_str = f" [{selected_items[item['title']]}]"
                        stdscr.addstr(y, x + len(item_str) + 1, qty_str)
                    
                    y += 1
            
            # Display total price of selected items
            stdscr.addstr(y + 2, w // 2 - 15, f"Total Price: ${total_price}")
            stdscr.addstr(y + 4, w // 2 - 15, "Press b or Backspace to go back.")
            stdscr.refresh()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # For highlighted items
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # For selected items

        print_menu(stdscr, current_row)
        
        while True:
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < total_items - 1:
                current_row += 1
            elif key == ord('b') or key == curses.KEY_BACKSPACE:
                if selected_items:
                    # Confirm exit with selected items
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 20, "You have selected items. Are you sure you want to leave?")
                    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press 'y' to leave, 'n' to continue.")
                    stdscr.refresh()
                    confirm_key = stdscr.getch()
                    if confirm_key == ord('y'):
                        selected_items.clear()  # Clear selected items if user confirms exit
                        break
                    else:
                        stdscr.clear()
                        print_menu(stdscr, current_row)
                else:
                    break
            elif key == ord('+'):
                # Add selected item to the order
                selected_item = menu[current_row // 5]['items'][current_row % 5]['title']
                if selected_item in selected_items:
                    selected_items[selected_item] += 1
                else:
                    selected_items[selected_item] = 1
                total_price += menu[current_row // 5]['items'][current_row % 5]['price']
            elif key == ord('-'):
                # Remove selected item from the order
                selected_item = menu[current_row // 5]['items'][current_row % 5]['title']
                if selected_item in selected_items and selected_items[selected_item] > 0:
                    selected_items[selected_item] -= 1
                    
                    total_price -= menu[current_row // 5]['items'][current_row % 5]['price']
                    if len(selected_items)==0:
                        total_price = 0
                    
                    if selected_items[selected_item] == 0:
                        del selected_items[selected_item]
            elif key == ord('a'):
                # Show options for table reservation and delivery
                payment_method = "Online"  # Default payment method
                stdscr.clear()
                stdscr.addstr(h // 2 - 5, w // 2 - 20, "Options before finalizing order:")
                stdscr.addstr(h // 2 - 3, w // 2 - 20, "1. Reserve a table")
                stdscr.addstr(h // 2 - 2, w // 2 - 20, "2. Send food outside of the restaurant")
                stdscr.addstr(h // 2 - 1, w // 2 - 20, f"3. Select payment method ( Default Option: {payment_method} )")
                stdscr.addstr(h // 2, w // 2 - 20, "Choose an option (1-2): ")
                stdscr.refresh()
                
                option = stdscr.getch()
                
                if option == ord('1'):
                    # Reserve a table option
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 15, "Reserve a Table")
                    stdscr.addstr(h // 2 + 1, w // 2 - 20, f"Total Price: ${total_price}")
                    stdscr.addstr(h // 2 + 2, w // 2 - 20, "Table numbers available: 1-9")
                    stdscr.addstr(h // 2 + 3, w // 2 - 20, "Unavailable tables: 3, 6, 9")
                    stdscr.addstr(h // 2 + 4, w // 2 - 20, "Enter table number to reserve: ")
                    stdscr.refresh()
                    
                    table_number = stdscr.getch()
                    
                    if table_number in range(ord('1'), ord('9') + 1):  # Assuming 1-2 for demo
                        stdscr.clear()
                        stdscr.addstr(h // 2, w // 2 - 10, f"Table {chr(table_number)} reserved!")
                        stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                        stdscr.refresh()
                        stdscr.getch()
                    else:
                        stdscr.clear()
                        stdscr.addstr(h // 2, w // 2 - 10, "Invalid table number!")
                        stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                        stdscr.refresh()
                        stdscr.getch()
                
                elif option == ord('2'):
                    # Send food outside of the restaurant option
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 20, "Send Food Outside of the Restaurant")
                    stdscr.addstr(h // 2 + 1, w // 2 - 20, "Enter delivery location coordinates (e.g., latitude, longitude): ")
                    stdscr.refresh()
                    
                    delivery_location = stdscr.getstr()
                    
                    # Logic to send food to delivery location (placeholder)
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 10, "Food sent to specified location!")
                    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                    stdscr.refresh()
                    stdscr.getch()
                elif option == ord('3'):
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 20, "Payment Methods:")
                    stdscr.addstr(h // 2 + 1, w // 2 - 20, "1. Online (Popular)")
                    stdscr.addstr(h // 2 + 2, w // 2 - 20, "2. Cash (In Person)")
                    stdscr.refresh()
                    
                    delivery_location = stdscr.getstr()
                    
                    # Logic to send food to delivery location (placeholder)
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 10, "")
                    stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                    stdscr.refresh()
                    stdscr.getch()


                # Finalize the order (placeholder action)
                stdscr.clear()
                stdscr.addstr(h // 2, w // 2 - 10, "Order finalized!")
                stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
            elif key == ord('/') or key == curses.ascii.ESC:
                # Search functionality: '/' or Escape key to enter search mode
                search_str = ""
                
                if search_str == "":
                    filtered_menu = [] 
                    for category in menu:
                        for item in category['items']:
                            filtered_menu.append(item)
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Search: {search_str}")  # Display current search term
                    y = 2  # Adjust starting y position based on search bar height
                    for idx, item in enumerate(filtered_menu):
                        x = w // 2 - 30
                        item_str = f"{item['title']}: ${item['price']}"
                        if item['title'] in selected_items:
                            item_str += " ✔"
                        if idx == current_row:
                            stdscr.attron(curses.color_pair(1))
                            stdscr.addstr(y, x, item_str)
                            stdscr.attroff(curses.color_pair(1))
                        else:
                            stdscr.addstr(y, x, item_str)
                        y += 1
                
                stdscr.refresh()

                # Capture user input for search
                while True:
                    search_key = stdscr.getch()

                    if search_key == curses.ascii.ESC:
                        break
                    elif search_key == 10:  # Enter key
                        break
                    elif search_key == curses.KEY_BACKSPACE:
                        search_str = search_str[:-1]
                    elif search_key >= 32 and search_key < 127:
                        search_str += chr(search_key)
                    # Filter menu items based on search string
                    filtered_menu=[]
                    for category in menu:
                        for item in category['items']:
                            if search_str.lower() in item['title'].lower():
                                filtered_menu.append(item)

                    # Display filtered menu
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Search: {search_str}")  # Display current search term
                    y = 2  # Adjust starting y position based on search bar height
                    for idx, item in enumerate(filtered_menu):
                        x = w // 2 - 30
                        item_str = f"{item['title']}: ${item['price']}"
                        if item['title'] in selected_items:
                            item_str += " ✔"
                        if idx == current_row:
                            stdscr.attron(curses.color_pair(1))
                            stdscr.addstr(y, x, item_str)
                            stdscr.attroff(curses.color_pair(1))
                        else:
                            stdscr.addstr(y, x, item_str)
                        y += 1
                    stdscr.addstr(h - 2, 0, f"Press '/' to search, 'b' to go back, Enter to select.")
                    stdscr.refresh()

                curses.curs_set(0)                    
                
            print_menu(stdscr, current_row)

    except FileNotFoundError:
        stdscr.addstr(h // 2, w // 2 - 10, "Menu file not found.")
        stdscr.addstr(h // 2 + 1, w // 2 - 10, "Press any key to return to main menu.")
        stdscr.refresh()
        stdscr.getch()
    except json.JSONDecodeError:
        stdscr.addstr(h // 2, w // 2 - 10, "Error decoding the menu file.")
        stdscr.addstr(h // 2 + 1, w // 2 - 10, "Press any key to return to main menu.")
        stdscr.refresh()
        stdscr.getch()

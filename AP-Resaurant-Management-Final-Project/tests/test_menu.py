import curses
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
        total_items = sum(min(len(category['items']), 5) for category in menu)  # Limit items to 5 per category

        def print_menu(stdscr, current_row):
            nonlocal total_price
            
            stdscr.clear()
            y = h // 2 - total_items // 2 - len(menu)
            
            for category in menu:
                stdscr.addstr(y, w // 2 - len(category['category']) // 2, category['category'], curses.A_BOLD)
                y += 2
                for idx, item in enumerate(category['items'][:5]):  # Display up to 5 items per category
                    x = w // 2 - 30
                    item_str = f"{item['title']}: ${item['price']}"
                    
                    # Add tick mark if item is selected
                    if item['title'] in selected_items:
                        item_str += " ✔"
                    
                    # Highlight selected items in a different color
                    if idx + y - (h // 2 - total_items // 2 - len(menu)) == current_row:
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
            elif key == ord('+') or key == ord('='):
                # Add selected item to the order
                selected_item = menu[current_row // len(menu)]['items'][current_row % len(menu)]['title']
                if selected_item in selected_items:
                    selected_items[selected_item] += 1
                else:
                    selected_items[selected_item] = 1
                total_price += menu[current_row // len(menu)]['items'][current_row % len(menu)]['price']
            elif key == ord('-'):
                # Remove selected item from the order
                selected_item = menu[current_row // len(menu)]['items'][current_row % len(menu)]['title']
                if selected_item in selected_items and selected_items[selected_item] > 0:
                    selected_items[selected_item] -= 1
                    total_price -= menu[current_row // len(menu)]['items'][current_row % len(menu)]['price']
                    if selected_items[selected_item] == 0:
                        del selected_items[selected_item]
            elif key == ord('a'):
                # Finalize the order and proceed to additional actions
                
                # Display finalize message
                stdscr.clear()
                stdscr.addstr(h // 2, w // 2 - 10, "Order finalized!")
                stdscr.addstr(h // 2 + 1, w // 2 - 15, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
                
                # Show options for table reservation and delivery
                stdscr.clear()
                stdscr.addstr(h // 2 - 5, w // 2 - 20, "Options after finalizing order:")
                stdscr.addstr(h // 2 - 3, w // 2 - 20, "1. Reserve a table")
                stdscr.addstr(h // 2 - 2, w // 2 - 20, "2. Send food outside of the restaurant")
                stdscr.addstr(h // 2, w // 2 - 20, "Choose an option (1-2): ")
                stdscr.refresh()
                
                option = stdscr.getch()
                
                if option == ord('1'):
                    # Reserve a table option
                    stdscr.clear()
                    stdscr.addstr(h // 2, w // 2 - 15, "Reserve a Table")
                    stdscr.addstr(h // 2 + 1, w // 2 - 20, f"Total Price: ${total_price}")
                    stdscr.addstr(h // 2 + 2, w // 2 - 20, "Table numbers available: 1-20")
                    stdscr.addstr(h // 2 + 3, w // 2 - 20, "Unavailable tables: 10, 12, 18")
                    stdscr.addstr(h // 2 + 4, w // 2 - 20, "Enter table number to reserve: ")
                    stdscr.refresh()
                    
                    table_number = stdscr.getch()
                    
                    if table_number in range(ord('1'), ord('2') + 1):  # Assuming 1-2 for demo
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

import curses, curses.ascii
from db.db import close_connection,connect_to_database
from db.models import User

def login(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 8, w//2 - len("Login Page")//2   , "Login Page", curses.A_BOLD | 1)
    stdscr.addstr(h//2 - 2, w//2 - 10, "Username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2 + 1).decode('utf-8')
    
    if username == "" or " " in username:
        return False ,"Invalid Username, it cant be empty or contains spaces.", None
    
    stdscr.addstr(h//2 - 1, w//2 - 10, "Password: ")
    password = stdscr.getstr(h//2 - 1, w//2 + 1).decode('utf-8')
    
    if password == "" or " " in password:
        return False, "Invalid Password, it cant be empty contains spaces.", None
    curses.noecho()

    # check whether user is in the db or not.
    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            user = User(id=result[0],username=result[1], password=result[2],isAdmin=result[3],
            location_lat=result[4],location_long=result[5])

            cursor.close()
            close_connection(connection)
            return True, "Welcome back, {}!".format(username), user
        else:
            cursor.close()
            close_connection(connection)
            return False, "Invalid username or password.", None

    else:
        return False, err, None
        

def register(stdscr):

    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h//2 - 8, w//2 - len("Register Page")//2   , "Register Page", curses.A_BOLD | 1)
    stdscr.addstr(h//2 - 2, w//2 - 20, "Choose a Username: ")
    curses.echo()
    username = stdscr.getstr(h//2 - 2, w//2).decode('utf-8')
    
    if username == "" or " " in username:
        return False ,"Invalid Username, it cant be empty or contains spaces.", None
    
    stdscr.addstr(h//2 - 1, w//2 - 20, "Choose a Password: ")
    password = stdscr.getstr(h//2 - 1, w//2).decode('utf-8')
    
    if password == "" or " " in password:
        return False, "Invalid Password, it cant be empty contains spaces.", None
    curses.noecho()
    
    connection, err = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            cursor.close()
            close_connection(connection)
            return False, "Username already exists.", None
        else:
            
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            connection.commit()

            user = User(username, password)
            cursor.close()
            close_connection(connection)
            return True, "User {} registered successfully!".format(user.username), user
    else:
        return False, "Something Went Wrong on Establishing Connection with DB.", None
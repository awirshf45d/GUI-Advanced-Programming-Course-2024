# db.py
import mysql.connector
from typing import Tuple, Union
from config.config import db_config

def connect_to_database() -> Tuple[Union[mysql.connector.connection.MySQLConnection, None], str]:
    try:
        connection = mysql.connector.connect(**db_config)
        return connection, ""
    except mysql.connector.Error as err:
        return None, "Error connecting to MySQL: {}".format(err)

def close_connection(connection : mysql.connector.connection.MySQLConnection) -> None:
    if connection:
        connection.close()

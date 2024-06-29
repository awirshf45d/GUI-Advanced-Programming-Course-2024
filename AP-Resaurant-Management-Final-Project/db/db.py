# db.py
import mysql.connector
from config.config import db_config

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection, ""
    except mysql.connector.Error as err:
        return None, "Error connecting to MySQL: {}".format(err)

def close_connection(connection):
    if connection:
        connection.close()

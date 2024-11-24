import datetime
import mysql.connector 

__cnx = None


def get_sql_connection():
    print("Opening mysql connection")
    global __cnx

    
    if __cnx is None:
        __cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='narc2004',
            database='grocerystore'
        )
    return __cnx

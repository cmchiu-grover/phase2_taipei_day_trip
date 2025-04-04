import time
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": "localhost",
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": "taipei_day_trip",
    "use_pure": True 
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  
    pool_reset_session=True,
    **dbconfig
)

def check_connect_periodically():
    while True:
        try:
            connection = connection_pool.get_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT 1")  
                cursor.close()
            connection.close()
        except Exception as e:
            print(e)
        time.sleep(14400)  # 每 10 分鐘檢查一次

if __name__ == "__main__":
    check_connect_periodically()

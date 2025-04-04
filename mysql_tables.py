from __future__ import print_function
from mysql_connect import get_connection_pool
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'taipei_day_trip'
TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  `email`  VARCHAR(255) NOT NULL,"
    "  `password` VARCHAR(255) NOT NULL,"
    "  `creation_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
    "  `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,"
    "  PRIMARY KEY (`id`), "
    "  UNIQUE KEY `unique_email` (`email`),"
    "  INDEX `index_email` (`email`)"
    ") ENGINE=InnoDB")

# TABLES['bookings'] = (
#     "CREATE TABLE `bookings` ("
#     "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
#     "  `user_id` INT(11) NOT NULL,"
#     "  `attraction_id` INT(11) NOT NULL,"
#     "  `booking_date` DATE NOT NULL,"
#     "  `booking_time` ENUM('gozen', 'gogo') NOT NULL,"
#     "  `price` INT(11) NOT NULL,"
#     "  `creation_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
#     "  `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,"
#     "  PRIMARY KEY (`id`),"
#     "  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,"
#     "  FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE,"
#     "  INDEX `index_booking_id` (`id`),"
#     "  INDEX `index_booking_date` (`booking_date`)"  
#     ") ENGINE=InnoDB")

cnx = get_connection_pool()
cursor = cnx.cursor(dictionary=True)

def create_database(cursor):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def check_database():
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("USE {}".format(DB_NAME))
        cursor.close()
        cnx.close()  
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
            cursor.close()
            cnx.close()  
        else:
            print(err)
            exit(1)

def create_tables():
    cnx = get_connection_pool()
    cursor = cnx.cursor(dictionary=True)
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    cursor.close()
    cnx.close()  

def mysql_main():
    check_database()
    create_tables()

if __name__ == "__main__":
    mysql_main()

# email = 'test001@gmail.com'

# existing_email = checkUsername('test001@gmail.com')

# print(existing_email)

# if existing_email == email:
#     print("email 已存在")
# else:
#     print("email 可使用")
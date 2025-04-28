from __future__ import print_function
from mysql_connect import get_connection_pool
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
load_dotenv()
DB_NAME = os.getenv("DATABASE")
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

TABLES['bookings'] = (
    "CREATE TABLE `bookings` ("
    "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
    "  `user_id` INT(11) NOT NULL,"
    "  `attraction_id` INT(11) NOT NULL,"
    "  `booking_date` DATE NOT NULL,"
    "  `booking_time` ENUM('morning', 'afternoon') NOT NULL,"
    "  `price` INT(11) NOT NULL,"
    "  `creation_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
    "  `updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE,"
    "  INDEX `index_booking_id` (`id`),"
    "  INDEX `index_booking_date` (`booking_date`)"  
    ") ENGINE=InnoDB")

TABLES['orders'] = (
   "CREATE TABLE orders ("
    "`order_id` VARCHAR(32),"
    "`user_id` INT(11) NOT NULL,"
    "`attraction_id` INT(11) NOT NULL,"
    "`order_date` DATE NOT NULL,"
    "`order_time` ENUM('morning', 'afternoon') NOT NULL,"
    "`price` INT(11) NOT NULL,"
    "`phone` VARCHAR(32) NOT NULL,"
    "`creation_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
    "`updated_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,"
    "`status` VARCHAR(32) NOT NULL DEFAULT 'UNPAID',"
    "PRIMARY KEY (`order_id`),"
    "FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,"
    "FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE,"
    "INDEX `index_user_id` (`user_id`),"
    "INDEX `index_attraction_id` (`attraction_id`)"
    ") ENGINE=InnoDB")

TABLES['mrt'] = (
   "CREATE TABLE mrt ("
    "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  INDEX `index_id` (`id`),"
    "  INDEX `index_name` (`name`)"
    ") ENGINE=InnoDB")

TABLES['category'] = (
   "CREATE TABLE category ("
    "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  INDEX `index_id` (`id`),"
    "  INDEX `index_name` (`name`)"
    ") ENGINE=InnoDB")

TABLES['attraction'] = (
   "CREATE TABLE attraction ("
    "  `id` INT(11) NOT NULL,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  `description` VARCHAR(10000) NOT NULL,"
    "  `address` VARCHAR(255) NOT NULL,"
    "  `transport` VARCHAR(1000) NOT NULL,"
    "  `rate` TINYINT CHECK (`rate` BETWEEN 1 AND 5),"
    "  `lat` DECIMAL(9,6)  NOT NULL,"
    "  `lng` DECIMAL(9,6)  NOT NULL,"
    "  `mrt_id` INT(11),"
    "  `category_id` INT(11) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`mrt_id`) REFERENCES `mrt` (`id`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE CASCADE,"
    "  INDEX `index_id` (`id`),"
    "  INDEX `index_mrt_id` (`mrt_id`),"
    "  INDEX `index_category_id` (`category_id`)"    
    ") ENGINE=InnoDB")

TABLES['images'] = (
   "CREATE TABLE images ("
    "  `id` INT(11) NOT NULL AUTO_INCREMENT,"
    "  `attraction_id` INT(11) NOT NULL,"
    "  `url` VARCHAR(255) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`) ON DELETE CASCADE,"
    "  INDEX `index_id` (`id`),"
    "  INDEX `index_attraction_id` (`attraction_id`),"
    "  INDEX `index_url` (`url`)"
    ") ENGINE=InnoDB")

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
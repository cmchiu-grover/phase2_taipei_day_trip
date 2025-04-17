from __future__ import print_function
from mysql_connect import get_connection_pool
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Header, Request
from datetime import datetime
# from fastapi.security import OAuth2PasswordBearer


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth")

cnx = get_connection_pool()
cursor = cnx.cursor(dictionary=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserForm:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def insertUser(self):
        try:
            cnx = get_connection_pool()
            cursor = cnx.cursor()

            insert_query = (
                "INSERT INTO `users` (`name`, `email`, `password`) "
                "VALUES (%s, %s, %s)"
            )

            cursor.execute(insert_query, (self.name, self.email, self.password))
            cnx.commit()

            print(f"User {self.email} inserted successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cnx.rollback()

        finally:
            try:
                cursor.close()
                cnx.close()
            except:
                pass
    
       
class BookingForm:
    def __init__(self, user_id, attraction_id, date, time, price):
        self.user_id = user_id
        self.attraction_id = attraction_id
        self.date = date
        self.time = time
        self.price = price

    def insert_booking(self):
        try:
            cnx = get_connection_pool()
            cursor = cnx.cursor()

            insert_query = (
                "INSERT INTO `bookings` (`user_id`, `attraction_id`, `booking_date`, `booking_time`, `price`) "
                "VALUES (%s, %s, %s, %s, %s)"
            )

            cursor.execute(insert_query, (self.user_id, self.attraction_id, self.date, self.time, self.price))
            cnx.commit()

            print(f"User {self.attraction_id} inserted successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cnx.rollback()

        finally:
            try:
                cursor.close()
                cnx.close()
            except:
                pass
    
    def update_booking(self):
        try:
            cnx = get_connection_pool()
            cursor = cnx.cursor()

            update_query = (
                "UPDATE `bookings` SET `attraction_id`=%s, `booking_date`=%s, `booking_time`=%s, `price`=%s WHERE `user_id` = %s "
            )

            cursor.execute(update_query, (self.attraction_id, self.date, self.time, self.price, self.user_id))
            cnx.commit()

            print(f"User's booking {self.attraction_id} updated successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cnx.rollback()

        finally:
            try:
                cursor.close()
                cnx.close()
            except:
                pass


def checkUser(new_email):
    try:
        cnx = get_connection_pool()  
        cursor = cnx.cursor(dictionary=True)  

        query = "SELECT id, name, email, password FROM users WHERE email = %s"
        cursor.execute(query, (new_email,))
        existing_user = cursor.fetchone()  

        if existing_user:  
            print("email 存在...")
            return existing_user
        else:
            print("回傳 None...")
            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def query_user_data(user_id):
    try:
        cnx = get_connection_pool()  
        cursor = cnx.cursor(dictionary=True)  

        query = "SELECT id, name, email FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        existing_user = cursor.fetchone()  

        if existing_user:  
            print("id 存在...")
            return existing_user
        else:
            print("回傳 None...")
            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass


def getPasswordHash(password):
    return pwd_context.hash(password)


def verifyPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def createAccessToken(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def getCurrentUser(request: Request):

    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split("Bearer ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        username: str = payload.get("username")
        email: str = payload.get("email")
        user_id: int = payload.get("user_id")
        if username is None or email is None or user_id is None:
            return None
        user = checkUser(email)  
        return user
    except Exception as e:
        print(e)
        return False

async def getCurrentActiveUser(request: Request):
    return await getCurrentUser(request)

def check_booking(user_id):
    try:
        cnx = get_connection_pool()  
        cursor = cnx.cursor(dictionary=True)  

        query = "SELECT id, user_id, attraction_id, booking_date, booking_time, price FROM bookings WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        existing_booking = cursor.fetchone()  

        if existing_booking:  
            print("已經有預定...")
            return existing_booking
        else:
            print("沒有預定...")
            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def delete_booking(user_id):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor()

        update_query = (
            "DELETE FROM `bookings` WHERE `user_id` = %s "
        )

        cursor.execute(update_query, (user_id,))
        cnx.commit()

        print(f"User ID: {user_id}'s booking deleted successfully.")

        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cnx.rollback()
        return False

    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass
        
def insertOrder(user_id: str, order_data: dict):
        try:
            cnx = get_connection_pool()
            cursor = cnx.cursor()

            insert_query = """
            INSERT INTO `orders` (
                `order_id`,
                `user_id`,
                `attraction_id`,
                `order_date`,
                `order_time`,
                `price`,
                `phone`

            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            order = order_data["order"]
            contact = order_data["order"]["contact"]
            attraction = order_data["order"]["trip"]["attraction"]

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

            order_id = f"{timestamp}-{attraction["id"]}-{user_id}"

            values = (
            order_id,       
            user_id,      
            attraction["id"],
            order["trip"]["date"],
            order["trip"]["time"],
            order["price"],
            contact["phone"],
            )

            cursor.execute(insert_query, values)
            cnx.commit()

            print(f"Order number: {order_id} inserted successfully.")
            return order_id

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cnx.rollback()

        finally:
            try:
                cursor.close()
                cnx.close()
            except:
                pass

def update_order_status(order_id: str):
        try:
            cnx = get_connection_pool()
            cursor = cnx.cursor()

            update_query = (
                "UPDATE `orders` SET `status`=%s WHERE order_id = %s"
            )

            cursor.execute(update_query, ("PAID", order_id))
            cnx.commit()

            print(f"Order number: {order_id} updated successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            cnx.rollback()

        finally:
            try:
                cursor.close()
                cnx.close()
            except:
                pass

def get_order_data(order_id: str):
    try:
        cnx = get_connection_pool()  
        cursor = cnx.cursor(dictionary=True)  

        query = "SELECT * FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        existing_order = cursor.fetchone()  

        if existing_order:  
            print("email 存在...")
            return existing_order
        else:
            print("回傳 None...")
            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

# asign_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QwMDIiLCJlbWFpbCI6InRlc3QwMDJAZ21haWwuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzQ0MDkwNTQyfQ.wx1QnQW3LgFadFc0we8m9sNG6Ql2LYAqfGccWjLRaVE"
# # user_dict = getCurrentUser(asign_token)
# # print(user_dict)

# payload_test = jwt.decode(asign_token, SECRET_KEY, algorithms=[ALGORITHM])
# print(payload_test)
from __future__ import print_function
from mysql_connect import get_connection_pool
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth")

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

    
def checkUser(new_email):
    try:
        cnx = get_connection_pool()  
        cursor = cnx.cursor(dictionary=True)  

        query = "SELECT id, name, email, password FROM users WHERE email = %s"
        cursor.execute(query, (new_email,))
        existing_user = cursor.fetchone()  
        cursor.close()
        cnx.close()

        if existing_user:  
            print("email 存在...")
            return existing_user
        else:
            print("回傳 None...")
            return None

    except Exception as e:
        print(f"錯誤: {e}")
        return None


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


def getCurrentUser(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        username: str = payload.get("username")
        email: str = payload.get("email")
        user_id: int = payload.get("user_id")
        if username is None or email is None or user_id is None:
            raise credentials_exception
        user = checkUser(email)  
        return user
    except:
        raise credentials_exception

async def getCurrentActiveUser(current_user: dict = Depends(getCurrentUser)):
    return current_user

# asign_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QwMDIiLCJlbWFpbCI6InRlc3QwMDJAZ21haWwuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzQ0MDkwNTQyfQ.wx1QnQW3LgFadFc0we8m9sNG6Ql2LYAqfGccWjLRaVE"
# # user_dict = getCurrentUser(asign_token)
# # print(user_dict)

# payload_test = jwt.decode(asign_token, SECRET_KEY, algorithms=[ALGORITHM])
# print(payload_test)
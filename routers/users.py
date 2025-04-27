from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from mysql_crud import UserForm, checkUser, getPasswordHash, verifyPassword, createAccessToken, getCurrentActiveUser
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

router = APIRouter()

@router.post("/api/user")
def signup(user_regis_data: dict = Body(...)):
    try:
        existing_user = checkUser(user_regis_data["email"])

        if existing_user: 
            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"電子郵件重複"
                    }
                    )
        
        password_hs256 = getPasswordHash(user_regis_data["password"])
        
        user_data = UserForm(user_regis_data["name"], user_regis_data["email"], password_hs256)

        user_data.insertUser()

        return JSONResponse(
            status_code=200,
            content={
                "ok": True
                }
                )
    except:
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )  

@router.put("/api/user/auth")
async def signin_form(user_data: dict = Body(...)):
    try:
        
        existing_user = checkUser(user_data.get("email"))
        print(existing_user)

        if not existing_user:
            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"查無使用者或密碼錯誤"
                    }
                    )
        
        
        if verifyPassword(user_data["password"], existing_user["password"]):
            access_token_expires = timedelta(days = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")))
            access_token = createAccessToken(
                data={
                    "username": existing_user["name"],
                    "email": existing_user["email"],
                    "user_id":existing_user["id"]
                    },
                    expires_delta = access_token_expires
                    )

            return JSONResponse(
                status_code=200,
                content={
                    "token": access_token
                    },
                    )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"查無使用者或密碼錯誤"
                    }
                    )
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )

@router.get("/api/user/auth")
async def get_user_data(request: Request):
    current_user = await getCurrentActiveUser(request)
    if not current_user:
        return JSONResponse(
            status_code=200,
            content = { "data": None
                }
                )

    return JSONResponse(
            status_code=200,
            content = { "data": {
                "id": current_user["id"],
                "name": current_user["name"],
                "email": current_user["email"]
                }
                }
                )

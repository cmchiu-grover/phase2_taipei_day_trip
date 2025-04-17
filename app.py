from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from mysql_connect import get_attraction_list_rank, get_mrt_list, get_attraction
import uvicorn
from mysql_crud import UserForm, checkUser, getPasswordHash, verifyPassword, createAccessToken, getCurrentActiveUser, BookingForm, check_booking, delete_booking, insertOrder, update_order_status, get_order_data, query_user_data
from datetime import timedelta
from dotenv import load_dotenv
import os
import requests
app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()



# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")

@app.get("/api/mrts")
def api_mrts():
    try:
        mrt_list = get_mrt_list()
        

        if not mrt_list:
            return JSONResponse(
                status_code=500,
                content={"error": True, "message": "伺服器錯誤..."}
            )

        return {"data": mrt_list}

    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器錯誤..."}
        )

@app.get("/api/attraction/{attractionId}")
def attraction(attractionId: int):
    try:
        attraction = get_attraction(attractionId)

        if not attraction:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "景點編號不正確或無此編號"}
            )

        return attraction

    except:
        return JSONResponse(
            status_code=500,
            content={"error": True,
                     "message":"伺服器錯誤..."}
                     )

@app.get("/api/attractions")
def get_attraction_list(
    page: int = Query(0, ge=0),
    keyword: str = None
    ):
    try:

        results = get_attraction_list_rank(page, keyword)[0]

        next_page = get_attraction_list_rank(page, keyword)[1]

        return {
            "nextPage": next_page,
            "data": [
                {
                    "id": attraction["id"],
                    "name": attraction["name"],
                    "category": attraction["CATEGORY_NAME"],
                    "description": attraction["description"],
                    "address": attraction["address"],
                    "transport": attraction["transport"],
                    "mrt": attraction["MRT_NAME"] if attraction["MRT_NAME"] else None,
                    "lat": float(attraction["lat"]),
                    "lng": float(attraction["lng"]),
                    "images": attraction["IMAGE_URLS"].split(',')
                }
                for attraction in results
            ]
        }
    except:
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )

@app.post("/api/user")
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

@app.put("/api/user/auth")
async def signin_form(user_data: dict = Body(...)):
    try:
        
        existing_user = checkUser(user_data.get("email"))
        print(existing_user)

        if not existing_user:
            # print("not existing_user")

            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"查無使用者或密碼錯誤"
                    }
                    )
        
        
        if verifyPassword(user_data["password"], existing_user["password"]):
            # print("Signup...")

            ACCESS_TOKEN_EXPIRE_DAYS = 7

            access_token_expires = timedelta(days = ACCESS_TOKEN_EXPIRE_DAYS)
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
    except:
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )

@app.get("/api/user/auth")
async def get_user_data(request: Request):
    current_user = await getCurrentActiveUser(request)
    # print(current_user)
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

@app.post("/api/booking")
async def book_one_attraction(request: Request,
    attr_data: dict = Body(...)
    ):
    current_user = await getCurrentActiveUser(request)
    try:
        # print(f"current_user is {current_user}")
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error": True,
                "message": "未登入系統，拒絕存取"
                }
                )

        user_id = current_user["id"]
        existing_booking = check_booking(user_id)
        # print(f"existing_booking is {existing_booking}")
        # print(f"attr_data is {attr_data}")

        try:
            booking_data = BookingForm(user_id,
                                        attr_data["attractionId"],
                                        attr_data["date"],
                                        attr_data["time"],
                                        attr_data["price"])
        except Exception as e:
            print(f"booking_data 失敗，error：{e}")
            return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": f"建立失敗，error：{e}"
                }
                )
        
        # print(f"booking_data is {booking_data}")

        if existing_booking:
            print("Booking 存在...")
            try:
                booking_data.update_booking()
                print("Booking updated...")
            except Exception as e:
                print(f"booking_data 更新失敗，error：{e}")
                return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"更新失敗，error：{e}"
                    }
                    )

        else:
            try:
                booking_data.insert_booking()
                print("Booking inserted...")
            except Exception as e:
                print(f"booking_data 建立失敗，error：{e}")
                return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"建立失敗，error：{e}"
                    }
                    )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True
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

@app.get("/api/booking")
async def get_booking_data(request: Request):
    current_user = await getCurrentActiveUser(request)
    try:
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error":True,
                "message": "未登入系統，拒絕存取"
                }
                )
        # print(f"開始取得預定資料...")
        user_id = current_user["id"]
        # print(f"預定的使用者為：{user_id}")
        existing_booking = check_booking(user_id)
        # print(f"existing_booking is {existing_booking}")

        if not existing_booking:
            return JSONResponse(
                status_code=200,
                content={
                    "data": None,
                }
        )

        

        attraction_data = get_attraction(existing_booking["attraction_id"])["data"]
        # print(f"attraction_data is {attraction_data}")
        # print(f"id = {existing_booking["attraction_id"]}")
        # print(f"name = {attraction_data["name"]}")
        # print(f"address = {attraction_data["address"]}")
        # print(f"image = {attraction_data["images"][0]}")
        # print(f"date = {existing_booking["booking_date"]}")
        # print(f"time = {existing_booking["booking_time"]}")
        # print(f"price = {existing_booking["price"]}")

        return JSONResponse(
            status_code=200,
            content={
                "data":{
                    "attraction":{
                        "id":existing_booking["attraction_id"],
                        "name":attraction_data["name"],
                        "address":attraction_data["address"],
                        "image":attraction_data["images"][0]

                    },
                    "date":existing_booking["booking_date"].strftime("%Y/%m/%d"),
                    "time":existing_booking["booking_time"],
                    "price":existing_booking["price"]
                }
            }
        )
    except Exception as e:
        print(f"伺服器錯誤：{e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器錯誤..."
            }
        )
        
@app.delete("/api/booking")
async def delete_booking_data(request: Request):
    current_user = await getCurrentActiveUser(request)
    print(current_user)
    try:
        print(f"開始刪除資料...，current_user is {current_user}")
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error": True,
                "message": "未登入系統，拒絕存取"
                }
                )

        user_id = current_user["id"]
        existing_booking = check_booking(user_id)
        # print(f"existing_booking is {existing_booking}")
        # print(f"attr_data is {attr_data}")       
        # print(f"booking_data is {booking_data}")

        if existing_booking:
            # print("Booking 存在，開始刪除...")
            if delete_booking(user_id):
                # print("Booking 刪除完畢...")
                return JSONResponse(
                status_code=200,
                content={
                    "ok": True
                    }
                    )
            else:
                # print("刪除時發生錯誤...")
                return JSONResponse(
                status_code=500,
                content={
                    "error":True,
                    "message":"伺服器錯誤..."
                    }
                    )  

        else:
            return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "並無預定的行程，無法刪除！"
                }
                )


    
    except Exception as e:
         print(f"伺服器錯誤：{e}")
         return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )  

@app.post("/api/orders")
async def book_one_attraction(request: Request,
    order_data: dict = Body(...)
    ):
    current_user = await getCurrentActiveUser(request)
    TAPPAY_URL = os.getenv("TAPPAY_URL")
    PARTNER_KEY = os.getenv("PARTNER_KEY")
    MERCHANT_ID = os.getenv("MERCHANT_ID")
    print(order_data["order"]["contact"])
    try:
        # print(f"current_user is {current_user}")
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error": True,
                "message": "未登入系統，拒絕存取"
                }
                )
        
        order_id = insertOrder(current_user["id"], order_data)
    
        # print(f"existing_booking is {existing_booking}")
        # print(f"attr_data is {attr_data}")      


        try:
            headers = {
            "Content-Type": "application/json",
            "x-api-key": PARTNER_KEY
            }
       
            payload = {
            "prime": order_data["prime"],
            "partner_key": PARTNER_KEY,
            "merchant_id": MERCHANT_ID,
            "details":"TapPay Test",
            "amount": order_data["order"]["price"],
            "cardholder": {
                "phone_number": order_data["order"]["contact"]["phone"],
                "name": order_data["order"]["contact"]["name"],
                "email": order_data["order"]["contact"]["email"],
            },
            }
            
            response = requests.post(TAPPAY_URL, headers=headers, json=payload)

            result = response.json()
            print(result)

            if result["status"] == 0:
                update_order_status(order_id)
            else:
                return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f'訂單編號：order_id\n付款失敗，請重新輸入信用卡付款資訊。\nError: {result["msg"]}.'
                    }
                    )

        except Exception as e:
            print(f"失敗，error：{e}")
            return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": f"建立失敗，error：{e}"
                }
                )

        return JSONResponse(
            status_code=200,
            content={
                "data": {
                "number": order_id,
                "payment": {
                "status": 0,
                "message": "付款成功"
                }
                }
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

@app.get("/api/order/{orderNumber}")
async def attraction(request: Request,orderNumber: str):
    try:
        current_user = await getCurrentActiveUser(request)
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error": True,
                "message": "未登入系統，拒絕存取"
                }
                )

        order_data = get_order_data(orderNumber)

        if not order_data:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "編號不正確或無此編號"}
            )
        
        status_code = 0 if order_data["status"] == "PAID" else 1

        attraction_data = get_attraction(order_data["attraction_id"])

        user_data = query_user_data(order_data["user_id"])

        return JSONResponse(
            status_code=200,
            content={
                    "data": {
                        "number": orderNumber,
                        "price": order_data["price"],
                        "trip": {
                        "attraction": {
                            "id": order_data["attraction_id"],
                            "name": attraction_data["data"]["name"],
                            "address": attraction_data["data"]["address"],
                            "image": attraction_data["data"]["images"][0]
                        },
                        "date": str(order_data["order_date"]),
                        "time": order_data["order_time"]
                        },
                        "contact": {
                        "name": user_data["name"],
                        "email": user_data["email"],
                        "phone": order_data["phone"]
                        },
                        "status": status_code
                    }
                    }
                     )

    except Exception as e:
        print(f"失敗，error：{e}")
        return JSONResponse(
            status_code=500,
            content={"error": True,
                     "message":"伺服器錯誤..."}
                     )

if __name__ == '__main__':
    uvicorn.run("app:app", port=8000, reload = True)
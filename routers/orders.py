from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from mysql_crud import getCurrentActiveUser, insertOrder, update_order_status, get_order_data, query_user_data
import requests
import os
from dotenv import load_dotenv
from mysql_connect import get_attraction
router = APIRouter()
load_dotenv()

@router.post("/api/orders")
async def book_one_attraction(request: Request,
    order_data: dict = Body(...)
    ):
    current_user = await getCurrentActiveUser(request)
    TAPPAY_URL = os.getenv("TAPPAY_URL")
    PARTNER_KEY = os.getenv("PARTNER_KEY")
    MERCHANT_ID = os.getenv("MERCHANT_ID")
    print(order_data["order"]["contact"])
    try:
        if not current_user:
            return JSONResponse(
            status_code=403,
            content={
                "error": True,
                "message": "未登入系統，拒絕存取"
                }
                )
        
        order_id = insertOrder(current_user["id"], order_data)

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

@router.get("/api/order/{orderNumber}")
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
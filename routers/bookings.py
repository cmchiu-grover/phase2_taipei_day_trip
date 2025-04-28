from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from mysql_crud import getCurrentActiveUser, check_booking, BookingForm, delete_booking
from mysql_connect import get_attraction
router = APIRouter()

@router.post("/api/booking")
async def book_one_attraction(request: Request,
    attr_data: dict = Body(...)
    ):
    current_user = await getCurrentActiveUser(request)
    try:
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

@router.get("/api/booking")
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
        
        user_id = current_user["id"]
        
        existing_booking = check_booking(user_id)
        

        if not existing_booking:
            return JSONResponse(
                status_code=200,
                content={
                    "data": None,
                }
        )

        attraction_data = get_attraction(existing_booking["attraction_id"])["data"]

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
        
@router.delete("/api/booking")
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

        if existing_booking:
            if delete_booking(user_id):
                return JSONResponse(
                status_code=200,
                content={
                    "ok": True
                    }
                    )
            else:
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

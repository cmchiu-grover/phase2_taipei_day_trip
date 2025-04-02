from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from tables import Attraction, Mrt, Category, Image, Base
from sqlalchemy.sql import func, case
from connection_pool import get_attraction_list_rank
from model import get_db
import uvicorn
from mysql_crud import UserForm, checkUser, getPasswordHash, verifyPassword, createAccessToken, getCurrentActiveUser

from datetime import timedelta

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

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
def get_mrt_list():
    try:

        with get_db() as db:
            subquery = (
                db.query(
                    Attraction.mrt_id,
                    func.count(Attraction.id).label("Attraction_Qty")
                    )
                    .filter(Attraction.mrt_id.isnot(None))
                    .group_by(Attraction.mrt_id)
                    .subquery()
                    )
            query = (
                db.query(
                    Mrt.name,
                    subquery.c.Attraction_Qty
                )
                .outerjoin(subquery, Mrt.id == subquery.c.mrt_id)
                .order_by(
                    case(
                        (subquery.c.Attraction_Qty.is_(None), 1),  # NULL 值排最後
                        else_=0
                    ),
                    subquery.c.Attraction_Qty.desc(),  # 依據 Attraction_Qty 排序
                    Mrt.id
                )
            )
        mrt_list = [mrt[0] for mrt in query.all()]
        
        if not mrt_list:
            return JSONResponse(
                status_code=500,
                content={
                    "error":True,
                    "message":"伺服器錯誤..."
                    }
                    )
        
        return {
            "data": mrt_list
            }
    
    except:
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message":"伺服器錯誤..."
                }
                )

@app.get("/api/attraction/{attractionId}")
def get_attraction(attractionId: int):
    try:
        with get_db() as db:


            attraction = db.query(Attraction).filter(Attraction.id == attractionId).first()

        if not attraction:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "景點編號不正確或無此編號"}
            )

        with get_db() as db:
            mrt = db.query(Mrt).filter(Mrt.id == attraction.mrt_id).first()
            category = db.query(Category).filter(Category.id == attraction.category_id).first()
            images = db.query(Image).filter(Image.attraction_id == attraction.id).all()
        
        image_urls = [img.url for img in images]
        

        return {
            "data": {
                "id": attraction.id,
                "name": attraction.name,
                "category": category.name if category else None,
                "description": attraction.description,
                "address": attraction.address,
                "transport": attraction.transport,
                "mrt": mrt.name if mrt else None,
                "lat": attraction.lat,
                "lng": attraction.lng,
                "images": image_urls
            }
        }

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
def signup(
    # request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    ):
    try:
        existing_user = checkUser(email)

        if existing_user: 
            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"電子郵件重複"
                    }
                    )
        
        password_hs256 = getPasswordHash(password)
        
        user_data = UserForm(name, email, password_hs256)

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

@app.post("/api/user/auth")
async def signin_form(
    # request: Request,
    email: str = Form(...),
    password: str = Form(...),
    ):
    try:

        existing_user = checkUser(email)

        if not existing_user:
            # print("not existing_user")

            return JSONResponse(
                status_code=400,
                content={
                    "error":True,
                    "message":"查無使用者或密碼錯誤"
                    }
                    )
        
        
        if verifyPassword(password, existing_user["password"]):
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
async def get_user_data(current_user: dict = Depends(getCurrentActiveUser)):
    # print(current_user)
    return JSONResponse(
            status_code=200,
            content = { "data": {
                "id": current_user["id"],
                "name": current_user["name"],
                "email": current_user["email"]
                }
                }
                )


# if __name__ == '__main__':
#     uvicorn.run("app:app", port=8000, reload = True)
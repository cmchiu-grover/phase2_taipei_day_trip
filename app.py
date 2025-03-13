from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from tables import Attraction, Mrt, Category, Image, Base
from sqlalchemy.sql import func, case
from sqlalchemy.orm import joinedload
from model import get_db
import uvicorn


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
    num_per_page: int = 12,
    keyword: str = None
    ):
    try:
        with get_db() as db:
            
            attraction_query = db.query(Attraction).options(
                joinedload(Attraction.category),
                joinedload(Attraction.images),
                joinedload(Attraction.mrt)
                )
                
            total_count = attraction_query.count()

            if page * num_per_page > total_count:
                return JSONResponse(
                status_code=500,
                content={"error": True, "message": "超出頁數..."}
                )

            attractions = attraction_query.all()

        if keyword:
            keyword_matches = [attraction for attraction in attractions if keyword.lower() in attraction.name.lower() or (attraction.description and keyword.lower() in attraction.description.lower())]
            keyword_matches.sort(key=lambda x: (-x.rate, x.id))  

            non_keyword_matches = [attraction for attraction in attractions if not (keyword.lower() in attraction.name.lower() or (attraction.description and keyword.lower() in attraction.description.lower()))]
            non_keyword_matches.sort(key=lambda x: (-x.rate, x.id))  

            sorted_results = keyword_matches + non_keyword_matches
            results = sorted_results[page * num_per_page : (page + 1) * num_per_page]
                
        else:
            results = attraction_query.offset(page * num_per_page).limit(num_per_page).all()


        next_page = page + 1 if (page + 1) * num_per_page < total_count else None

        return {
            "nextPage": next_page,
            "data": [
                {
                    "id": attraction.id,
                    "name": attraction.name,
                    "category": attraction.category.name,
                    "description": attraction.description,
                    "address": attraction.address,
                    "transport": attraction.transport,
                    "mrt": attraction.mrt.name if attraction.mrt else None,
                    "lat": float(attraction.lat),
                    "lng": float(attraction.lng),
                    "images": [img.url for img in attraction.images]
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
            

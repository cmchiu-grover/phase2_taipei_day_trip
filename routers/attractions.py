from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from mysql_connect import get_attraction_list_rank, get_attraction, get_mrt_list

router = APIRouter()

@router.get("/api/attraction/{attractionId}")
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

@router.get("/api/attractions")
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


@router.get("/api/mrts")
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


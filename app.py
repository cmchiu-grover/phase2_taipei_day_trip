from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from routers.attractions import router as attractions_router
from routers.users import router as users_router
from routers.bookings import router as bookings_router
from routers.orders import router as orders_router
app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(attractions_router)
app.include_router(users_router)
app.include_router(bookings_router)
app.include_router(orders_router)

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


# if __name__ == '__main__':
#     uvicorn.run("app:app", port=8000, reload = True)
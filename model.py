import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from tables import Attraction, Mrt, Category, Image, Base
import json
from json import load

print(os.getcwd())

load_dotenv()
MySQL_DB_URL = os.getenv("MySQL_DB_URL")

engine = create_engine(
    MySQL_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,  
    pool_pre_ping=True   
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(engine)

def spiltUrl(url):
    img_url_list = re.findall(r'https?://[^\s]+?\.(?:jpg|JPG|png|PNG)', url)
    return img_url_list

def insert2Tables():
    with open("data/taipei-attractions.json", "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)
    results_list = data.get("result").get("results")
    with get_db() as db:
        for result in results_list:
            mrt_name = result.get("MRT")
            mrt_id = None
            if mrt_name:
                mrt = db.query(Mrt).filter(Mrt.name == mrt_name).first()
                if not mrt:
                    mrt = Mrt(name=mrt_name)
                    db.add(mrt)
                    db.commit()
                    db.refresh(mrt)
                mrt_id = mrt.id
            
            category_name = result.get("CAT")
            category_id = None
            if category_name:
                category = db.query(Category).filter(Category.name == category_name).first()
                if not category:
                    category = Category(name=category_name)
                    db.add(category)
                    db.commit()
                    db.refresh(category)
                category_id = category.id
            
            attraction = db.query(Attraction).filter(Attraction.name == result["name"]).first()
            if not attraction:
                new_attraction = Attraction(
                    id = int(result["_id"]),
                    name = result["name"],
                    description = result["description"],
                    address = result["address"],
                    transport = result["direction"],
                    rate = result["rate"],
                    lat = result["latitude"],
                    lng = result["longitude"],
                    mrt_id=mrt_id,
                    category_id=category_id
                    )
                db.add(new_attraction)
                db.commit()
                db.refresh(new_attraction)

                if "file" in result:
                    image_urls = spiltUrl(result["file"])
                    for url in image_urls:
                        new_image = Image(attraction_id=new_attraction.id, url=url)
                        db.add(new_image)

                db.commit()
    
    print("資料插入完成！")

if __name__ == "__main__":
    insert2Tables()
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": "localhost",
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("DATABASE"),
    "use_pure": True 
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    **dbconfig
)


def get_connection_pool():
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            return connection
        else:
            return connection_pool.get_connection()
    except Exception as e:
        print(e)
        return None
    

def get_attraction_list_rank(page: int, keyword: str = ''):
    num_per_page: int = 12

    start_num = (page)*num_per_page
    

    # print("Start...")
    conn = get_connection_pool()
    cursor = conn.cursor(dictionary=True)
    
    if not keyword:
        cursor.execute(f"""
            SELECT c.id, c.name, c.description, 
            c.address, c.transport, c.rate, 
            c.lat, c.lng, d.name AS MRT_NAME, 
            e.name AS CATEGORY_NAME, 
            GROUP_CONCAT(DISTINCT f.url SEPARATOR ',') AS IMAGE_URLS
            FROM attraction c 
            LEFT JOIN mrt d ON c.mrt_id = d.id 
            LEFT JOIN category e ON c.category_id = e.id 
            LEFT JOIN images f ON c.id = f.attraction_id
            GROUP BY c.id, d.name, e.name
            ORDER BY c.rate DESC, c.id ASC
            LIMIT {num_per_page} OFFSET {start_num};
                   """)
    else:
        cursor.execute(f"""
                SELECT c.id, c.name, c.description, 
                c.address, c.transport, c.rate, 
                c.lat, c.lng, d.name AS MRT_NAME, 
                e.name AS CATEGORY_NAME, 
                GROUP_CONCAT(DISTINCT f.url SEPARATOR ',') AS IMAGE_URLS,
                CASE 
                    WHEN d.name = '{keyword}' THEN 1   
                    WHEN c.name LIKE '%{keyword}%' THEN 2 
                    ELSE 3                     
                END AS `RANK`
                FROM attraction c 
                LEFT JOIN mrt d ON c.mrt_id = d.id 
                LEFT JOIN category e ON c.category_id = e.id 
                LEFT JOIN images f ON c.id = f.attraction_id
                WHERE d.name = '{keyword}' OR c.name LIKE '%{keyword}%'
                GROUP BY c.id, d.name, e.name
                ORDER BY `RANK` ASC, c.rate DESC, c.id ASC
                LIMIT {num_per_page} OFFSET {start_num};
                    """)
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()  


    # print(results)

    

    next_page = page + 1 if len(results) == num_per_page else None


    
    return [results, next_page]


def get_mrt_list():
    
    conn = get_connection_pool()
    cursor = conn.cursor()

    sql = """
        SELECT mrt.name, COUNT(attraction.id) AS qty
        FROM mrt
        LEFT JOIN attraction ON mrt.id = attraction.mrt_id
        GROUP BY mrt.id
        ORDER BY 
            qty IS NULL,
            qty DESC,
            mrt.id
    """
    cursor.execute(sql)
    mrt_list = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if not mrt_list:
        return None

    return mrt_list


def get_attraction(attractionId: int):
    try:
        conn = get_connection_pool()
        cursor = conn.cursor(dictionary=True)

        # 查 attraction
        cursor.execute("SELECT * FROM attraction WHERE id = %s", (attractionId,))
        attraction = cursor.fetchone()

        if not attraction:
            return None

        # 查 category 名稱
        cursor.execute("SELECT name FROM category WHERE id = %s", (attraction["category_id"],))
        category = cursor.fetchone()

        # 查 mrt 名稱
        if attraction["mrt_id"]:
            cursor.execute("SELECT name FROM mrt WHERE id = %s", (attraction["mrt_id"],))
            mrt = cursor.fetchone()
        else:
            mrt = None

        # 查 image URLs
        cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attractionId,))
        images = cursor.fetchall()
        image_urls = [img["url"] for img in images]

        return {
            "data": {
                "id": attraction["id"],
                "name": attraction["name"],
                "category": category["name"] if category else None,
                "description": attraction["description"],
                "address": attraction["address"],
                "transport": attraction["transport"],
                "mrt": mrt["name"] if mrt else None,
                "lat": float(attraction["lat"]),
                "lng": float(attraction["lng"]),
                "images": image_urls
            }
        }

    except Exception as e:
        print(e)
        return None

    finally:
        cursor.close()
        conn.close()



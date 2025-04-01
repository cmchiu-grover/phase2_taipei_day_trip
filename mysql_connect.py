from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": "localhost",
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": "taipei_day_trip",
    "use_pure": True 
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  
    **dbconfig
)


def get_connection_pool():
    return connection_pool.get_connection()

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


# cnx = get_connection_pool()
# cursor = cnx.cursor(dictionary=True)

# if cnx and cnx.is_connected():

#     with cnx.cursor() as cursor:

#         result = cursor.execute("SHOW tables;")

#         rows = cursor.fetchall()

#         print(f"以下為可使用的 tables（共有 {len(rows)} 張）：")

#         for rows in rows:

#             print(rows)

#     cursor.close()
#     cnx.close()

# else:

#     print("Could not connect")

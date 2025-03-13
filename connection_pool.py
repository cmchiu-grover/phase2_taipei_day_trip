from mysql.connector import pooling
import mysql.connector
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

def get_attraction_list_rank(page, keyword):
    num_per_page: int = 12
    
    print("Start...")
    conn = get_connection_pool()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
                   SELECT 
                    c.*, 
                    d.name AS MRT_NAME, 
                    e.name AS CATEGORY_NAME, 
                    GROUP_CONCAT(f.url) AS IMAGE_URLS
                    FROM attraction c 
                    LEFT JOIN mrt d ON c.mrt_id = d.id 
                    LEFT JOIN category e ON c.category_id = e.id 
                    LEFT JOIN images f ON c.id = f.attraction_id 
                    WHERE c.name LIKE '%{keyword}%'
                    GROUP BY c.id 
                    ORDER BY c.rate DESC, c.id ASC;
                   """)
    results1 = cursor.fetchall()

    cursor.execute(f"""
                   SELECT 
                    c.*, 
                    d.name AS MRT_NAME, 
                    e.name AS CATEGORY_NAME, 
                    GROUP_CONCAT(f.url) AS IMAGE_URLS
                    FROM attraction c 
                    LEFT JOIN mrt d ON c.mrt_id = d.id 
                    LEFT JOIN category e ON c.category_id = e.id 
                    LEFT JOIN images f ON c.id = f.attraction_id 
                    WHERE c.name NOT LIKE '%{keyword}%'
                    GROUP BY c.id 
                    ORDER BY c.rate DESC, c.id ASC;
                   """)

    results2 = cursor.fetchall()
    cursor.close()
    conn.close()  

    results = [*results1, *results2]

    print(results)

    total_count = len(results)

    next_page = page + 1 if (page + 1) * num_per_page < total_count else None

    start_num = (page)*num_per_page
    end_num = (page+1)*num_per_page

    return [results[start_num:end_num], next_page]




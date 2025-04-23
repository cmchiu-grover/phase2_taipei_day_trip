from mysql_connect import get_connection_pool
import re
from dotenv import load_dotenv
from contextlib import contextmanager
from mysql_crud import Attraction, Image
import json
from json import load



def spiltUrl(url):
    img_url_list = re.findall(r'https?://[^\s]+?\.(?:jpg|JPG|png|PNG)', url)
    return img_url_list

def query_mrt_name(mrt_name):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT * FROM mrt_test WHERE name = %s"
        cursor.execute(query, (mrt_name,))
        existing_mrt = cursor.fetchone()
        if existing_mrt:  
            print("mrt 存在...")
            return existing_mrt
        else:
            print("回傳 None...")
            return None
    
    except Exception as e:
        print(f"錯誤：{e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def insert_mrt_name(mrt_name):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        insert_query = """
            INSERT INTO `mrt_test` (
                `name`
            ) VALUES (%s)
            """
        cursor.execute(insert_query, (mrt_name,))
        cnx.commit()

        new_mrt_id = cursor.lastrowid
        print(f"MRT name '{mrt_name}' inserted successfully with id {new_mrt_id}.")
        return {"id": new_mrt_id}
    
    except Exception as e:
        print(f"錯誤：{e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def query_category_name(category_name):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT * FROM category_test WHERE name = %s"
        cursor.execute(query, (category_name,))
        existing_category = cursor.fetchone()
        if existing_category:  
            print("category 存在...")
            return existing_category
        else:
            print("回傳 None...")
            return None
    
    except Exception as e:
        print(f"錯誤：{e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def insert_category_name(category_name):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        insert_query = """
            INSERT INTO `category_test` (
                `name`
            ) VALUES (%s)
            """
        cursor.execute(insert_query, (category_name,))
        cnx.commit()

        new_category_id = cursor.lastrowid
        print(f"Category name '{category_name}' inserted successfully with id {new_category_id}.")
        return {"id": new_category_id}
    
    except Exception as e:
        print(f"錯誤：{e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

def query_attraction_name(attraction_name):
    try:
        cnx = get_connection_pool()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT * FROM attraction_test WHERE name = %s"
        cursor.execute(query, (attraction_name,))
        existing_attraction = cursor.fetchone()
        if existing_attraction:  
            print("attraction 存在...")
            return existing_attraction
        else:
            print("回傳 None...")
            return None
    
    except Exception as e:
        print(f"錯誤：{e}")
        return None
    
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass


def insert2Tables():
    with open("data/taipei-attractions.json", "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)
    results_list = data.get("result").get("results")

    for result in results_list:
        # print(f"===========開始 {result["name"]}==============")
        mrt_name = result.get("MRT")
        mrt_id = None
        if mrt_name:
            mrt_data = query_mrt_name(mrt_name)
            if not mrt_data:
                new_mrt_id = insert_mrt_name(mrt_name)
                mrt_id = new_mrt_id["id"]
            else:
                mrt_id = mrt_data["id"]
        
        category_name = result.get("CAT")
        category_id = None
        if category_name:
            category_data = query_category_name(category_name)
            
            if not category_data:
                new_category_id = insert_category_name(category_name)
                category_id = new_category_id["id"]
            else:
                category_id = category_data["id"]
        
        attraction = query_attraction_name(result["name"])
        if not attraction:
            new_attraction = Attraction(
                result["_id"],
                result["name"],
                result["description"],
                result["address"],
                result["direction"],
                result["rate"],
                result["latitude"],
                result["longitude"],
                mrt_id,
                category_id
                )

            new_attraction_id = new_attraction.insert_attraction()
            print(new_attraction_id)

            if "file" in result:
                image_urls = spiltUrl(result["file"])
                for url in image_urls:
                    new_image = Image(new_attraction_id, url)
                    new_image.insert_image()

    print("資料插入完成！")

if __name__ == "__main__":
    insert2Tables()
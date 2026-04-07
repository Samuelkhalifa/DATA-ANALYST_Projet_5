import requests
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

def get_api_results():

    url = "https://api.apitube.io/v1/news/everything"
    headers = {"X-API-Key": os.getenv("API_KEY")}
    #params = {"title": "climate","language.code": "en", "per_page": 5}
    response = requests.get(url, headers=headers)
    raw_data = response.json()

    return raw_data



def transform_data(raw_data):

    transformed_data = []

    for i in raw_data["results"]:
        i_transformed = {
            "link": i.get("href"),
            "language": (i.get("language").get("name") if isinstance(i.get("language"), dict) else i.get("language")),
            "published_at": i.get("published_at"),
            "title": i.get("title"),
            "description": i.get("description"),
            "body": i.get("body"),
            "author": i.get("author", {}).get("name"),
            "category": i.get("categories"[0], {}).get("name"),
            "topic": i.get("topics"[0], {}).get("name")
        }
        transformed_data.append(i_transformed)

    return transformed_data



def load_data_into_db(transformed_data):

    mysql_host = os.getenv("MYSQL_HOST")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_db_name = os.getenv("MYSQL_DB_NAME")
    mysql_table = os.getenv("MYSQL_TABLE")

    config = {
        "host": mysql_host,
        "user": mysql_user,
        "password": mysql_password
    }

    con = mysql.connector.connect(**config)
    cursor = con.cursor()

    cursor.execute(f"""
        CREATE DATABASE IF NOT EXISTS {mysql_db_name}
    """)
    cursor.execute(f"""
        USE {mysql_db_name}
    """)
    cursor.execute(f"""
        DROP TABLE IF EXISTS {mysql_table}
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {mysql_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            link VARCHAR(255),
            language VARCHAR(50),
            published_at VARCHAR(50),
            title VARCHAR(255),
            description TEXT,
            body TEXT,
            author VARCHAR(50),
            category VARCHAR(50),
            topic VARCHAR(50)
        )               
    """)
    values = [(d["link"], d["language"], d["published_at"], d["title"], d["description"], d["body"], d["author"], d["category"], d["topic"]) for d in transformed_data]
    cursor.executemany(f"""
        INSERT INTO {mysql_table} (link, language, published_at, title, description, body, author, category, topic)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, values)
    
    con.commit()
    cursor.close()
    con.close()



def main():
    raw_data = get_api_results()
    transformed_data = transform_data(raw_data)
    load_data_into_db(transformed_data)



main()
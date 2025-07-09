import time
import uuid
from datetime import datetime, timedelta
import requests
import psycopg2

def create_table(cursor):
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                gender VARCHAR(255),
                address VARCHAR(255),
                post_code VARCHAR(255),
                email VARCHAR(255),
                username VARCHAR(255),
                dob TIMESTAMP,
                registered_date TIMESTAMP,
                phone VARCHAR(255),
                picture VARCHAR(255)
            )
        """
    )

def insert_data(connection, cursor, data):
    data['dob'] = datetime.fromisoformat(data['dob'].replace('Z', '+00:00'))
    data['registered_date'] = datetime.fromisoformat(data['registered_date'].replace('Z', '+00:00'))
    data['post_code'] = str(data['post_code'])

    cursor.execute("""
        INSERT INTO users (id, first_name, last_name, gender, address, post_code, email, username, dob, registered_date, phone, picture)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [data["id"], data["first_name"], data["last_name"], data["gender"], data["address"], data["post_code"], data["email"],
          data["username"], data["dob"], data["registered_date"], data["phone"], data["picture"]])

    connection.commit()

def generate_user_data():
    response = requests.get("https://randomuser.me/api/").json()
    result = response['results'][0]
    data = format_data(result)

    return data

def format_data(res):
    data = {}
    location = res['location']
    data['id'] = str(uuid.uuid4())
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{location['street']['number']} {location['street']['name']}, {location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['large']

    return data

if __name__ == "__main__":
    connection = psycopg2.connect(
        host="localhost",
        port=5433,
        user="admin",
        password="postgres",
        database="userdb"
    )

    cursor = connection.cursor()

    # Generate data
    create_table(cursor)

    start_time = datetime.now()
    while True:
        if datetime.now() > start_time + timedelta(minutes=5):
            break

        data = generate_user_data()
        print(data)
        insert_data(connection, cursor, data)
        time.sleep(0.5)

    cursor.close()
    connection.close()
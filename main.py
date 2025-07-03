import time
import uuid
from datetime import datetime, timedelta
import requests
import oracledb

def create_table(cursor):
    try:
        cursor.execute(
            """
                CREATE TABLE users (
                    id VARCHAR2(255) PRIMARY KEY,
                    first_name VARCHAR2(255),
                    last_name VARCHAR2(255),
                    gender VARCHAR2(255),
                    address VARCHAR2(255),
                    post_code VARCHAR2(255),
                    email VARCHAR2(255),
                    username VARCHAR2(255),
                    dob TIMESTAMP,
                    registered_date TIMESTAMP,
                    phone VARCHAR2(255),
                    picture VARCHAR2(255)
                )
            """
        )
    except Exception as err:
        print(f"Table already exists: {err}")

def insert_data(connection, cursor, data):
    data['dob'] = datetime.fromisoformat(data['dob'].replace('Z', '+00:00'))
    data['registered_date'] = datetime.fromisoformat(data['registered_date'].replace('Z', '+00:00'))
    data['post_code'] = str(data['post_code'])

    cursor.execute("""
        INSERT INTO users (id, first_name, last_name, gender, address, post_code, email, username, dob, registered_date, phone, picture)
        VALUES (:id, :first_name, :last_name, :gender, :address, :post_code, :email, :username, :dob, :registered_date, :phone, :picture)
    """, data)

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
    connection = oracledb.connect(
        user="tricao",
        password="oracledb",
        dsn="localhost:1521/XEPDB1"
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
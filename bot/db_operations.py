from matplotlib.pyplot import get
import psycopg2
import psycopg2.extras
import os

params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

def find_user(id):
    global params
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect("host={host} user={user} password={password}".format(**params))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id=%s', (id,))
        result = cursor.fetchone()
        
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)

def get_departments():
    global params
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect("host={host} user={user} password={password}".format(**params))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT department_id, name FROM departments')
        result = cursor.fetchall()
        
        return dict(result)
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)

def add_user(data):
    global params
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect("host={host} user={user} password={password}".format(**params))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('INSERT INTO users (user_id, first_name, second_name, middle_name, department_id) \
            VALUES (%s, %s, %s, %s, %s)', (data))
        conn.commit()
        # cursor.execute('SELECT * FROM users')
        # print(cursor.fetchall())
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
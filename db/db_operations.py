import psycopg2
import psycopg2.extras
import os

params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

def find_user(id: int) -> tuple:
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id=%s', (id,))
        result = cursor.fetchone()
        
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return tuple()

def get_departments() -> dict():
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT department_id, name FROM departments')
        result = cursor.fetchall()
        
        return dict(result)
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return dict()

def get_categories() -> dict():
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT category_id, name FROM categories')
        result = cursor.fetchall()
        
        return dict(result)
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return dict()

def add_user(id: int, nickname: str) -> bool:
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('INSERT INTO users (user_id, nick) \
            VALUES (%s, %s)', (id, nickname))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False

def add_fio(data: dict) -> bool:
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET first_name = %s, second_name = %s, middle_name = %s, admin = %s \
            WHERE user_id=%s""", (data['first_name'], data['second_name'], data['middle_name'], data['admin'], data['user_id']))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False

def add_department(user_id: int, dep: int) -> bool:
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET department_id=%s \
            WHERE user_id=%s""", (dep, user_id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False



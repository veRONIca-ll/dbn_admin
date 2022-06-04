import psycopg2
import psycopg2.extras
import os

params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

def get_user(id: int) -> tuple:
    ''' Получение пользователя по ID '''
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

def get_departments() -> dict:
    ''' Получение всех отделов'''
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

def get_department_name(dep_id: int) -> tuple:
    ''' Получение название отдела по ID'''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT name FROM departments WHERE department_id=%s', (dep_id,))
        result = cursor.fetchone()
        
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return tuple()

def get_admins_id() -> tuple:
    ''' Получение ID всех экспертов '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT user_id FROM users WHERE admin=%s', (True,))
        result = cursor.fetchall()
        
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return tuple()
    finally:
        if conn is not None:
            conn.close()

def get_categories() -> dict:
    ''' Получение ID и названия всех категорий '''
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

def get_unsolved_tasks() -> tuple:
    ''' Получение нерешенных задач '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT card_id FROM tasks WHERE status=%s', (False,))
        result = cursor.fetchall()
        
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return tuple()

def add_user(id: int, nickname: str) -> bool:
    ''' Добавление нового пользователя по nickname'''
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

def update_user_fio(data: dict) -> bool:
    ''' Добавление ФИО пользователю '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET first_name = %s, second_name = %s, middle_name = %s \
            WHERE user_id=%s""", (data['first_name'], data['second_name'], data['middle_name'], data['user_id']))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False

def update_user_admin(id: int) -> bool:
    ''' Установка статуса admin пользователю '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET admin = %s \
            WHERE user_id=%s""", (True, id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False

def update_user_department(user_id: int, dep_id: int) -> bool:
    ''' Добавление ID отдела пользователю '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET department_id=%s \
            WHERE user_id=%s""", (dep_id, user_id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False


def add_task(user_id: int, cat_id: int, card_id: str, desc: str) -> bool:
    ''' Добавление задачи '''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""\
            INSERT INTO tasks (card_id, description, status, category_id, user_id) \
            VALUES (%s, %s, %s, %s, %s)""", (card_id, desc, False, cat_id, user_id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()

def update_task(card_id: str, steps: str) -> bool:
    ''' Обновление задачи: добавление описания и обновление статуса'''
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE tasks SET steps = %s, status=%s \
            WHERE card_id=%s""", (steps, True, card_id))
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
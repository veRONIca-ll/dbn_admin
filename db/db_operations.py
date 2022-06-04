import psycopg2
import psycopg2.extras
import os
from utils.logger import debug, err, info

params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

def get_user(id: int) -> tuple:
    ''' Получение пользователя по ID '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению ID пользователя')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id=%s', (id,))
        result = cursor.fetchone()

        debug('db', 'Конец работы с БД по получению ID пользователя')

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении ID пользователя: {error}')
        return tuple()
    finally:
        if conn is not None:
            conn.close()

def get_departments() -> dict:
    ''' Получение всех отделов'''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению всех отделов')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT department_id, name FROM departments')
        result = cursor.fetchall()

        debug('db', 'Конец работы с БД по получению всех отделов')

        return dict(result)
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении ID пользователя: {error}')
        return dict()
    finally:
        if conn is not None:
            conn.close()

def get_department_name(dep_id: int) -> tuple:
    ''' Получение название отдела по ID'''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению названия отдела по ID')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT name FROM departments WHERE department_id=%s', (dep_id,))
        result = cursor.fetchone()

        debug('db', 'Конец работы с БД по получению названия отдела по ID')

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении названия отдела по ID: {error}')
        return tuple()
    finally:
        if conn is not None:
            conn.close()

def get_admins_id() -> tuple:
    ''' Получение ID всех экспертов '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению ID всех экспертов')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT user_id FROM users WHERE admin=%s', (True,))
        result = cursor.fetchall()

        debug('db', 'Конец работы с БД по получению ID всех экспертов')

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении ID всех экспертов: {error}')
        return tuple()
    finally:
        if conn is not None:
            conn.close()

def get_categories() -> dict:
    ''' Получение ID и названия всех категорий '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению ID и названия всех категорий')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT category_id, name FROM categories')
        result = cursor.fetchall()

        debug('db', 'Конец работы с БД по получению ID и названия всех категорий')

        return dict(result)
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении ID и названия всех категорий: {error}')
        return dict()
    finally:
        if conn is not None:
            conn.close()

def get_unsolved_tasks() -> tuple:
    ''' Получение нерешенных задач '''
    global connection_para
    conn = None
    try:
        debug('db', 'Начало работы с БД по получению нерешенных задач')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT card_id FROM tasks WHERE status=%s', (False,))
        result = cursor.fetchall()

        debug('db', 'Конец работы с БД по получению нерешенных задач')

        return result
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при получении нерешенных задач: {error}')
        return tuple()
    finally:
        if conn is not None:
            conn.close()

def add_user(id: int, nickname: str) -> bool:
    ''' Добавление нового пользователя по nickname'''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по добавлению нового пользователя по nickname')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('INSERT INTO users (user_id, nick) \
            VALUES (%s, %s)', (id, nickname))
        conn.commit()
        info('db', f'Успешно добавлен пользователь: {id}')
        debug('db', 'Конец работы с БД по добавлению нового пользователя по nickname')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при добавлении нового пользователя по nickname: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

def update_user_fio(data: dict) -> bool:
    ''' Добавление ФИО пользователю '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по добавлению ФИО пользователю')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET first_name = %s, second_name = %s, middle_name = %s \
            WHERE user_id=%s""", (data['first_name'], data['second_name'], data['middle_name'], data['user_id']))
        conn.commit()
        info('db', f"Успешно добавлено ФИО пользователю: {data['user_id']}")
        debug('db', 'Конец работы с БД по добавлению ФИО пользователю')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при добавлении ФИО пользователю: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

def update_user_admin(id: int) -> bool:
    ''' Установка статуса admin пользователю '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по установке статуса admin пользователю')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET admin = %s \
            WHERE user_id=%s""", (True, id))
        conn.commit()

        info('db', f"Успешно обновлен статус пользователя: {id}")
        debug('db', 'Конец работы с БД по установке статуса admin пользователю')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при установке статуса admin пользователю: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

def update_user_department(user_id: int, dep_id: int) -> bool:
    ''' Добавление ID отдела пользователю '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по добавлению ID отдела пользователю')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE users SET department_id=%s \
            WHERE user_id=%s""", (dep_id, user_id))
        conn.commit()

        info('db', f"Успешно добавлен отдел пользователю: {user_id}")
        debug('db', 'Конец работы с БД по добавлению ID отдела пользователю')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при добавлении ID отдела пользователю: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

def add_task(user_id: int, cat_id: int, card_id: str, desc: str) -> bool:
    ''' Добавление задачи '''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по добавлению задачи')

        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""\
            INSERT INTO tasks (card_id, description, status, category_id, user_id) \
            VALUES (%s, %s, %s, %s, %s)""", (card_id, desc, False, cat_id, user_id))
        conn.commit()

        info('db', f"Успешно добавлена задача")
        debug('db', 'Конец работы с БД по добавлению задачи')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при добавлении задачи: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

def update_task(card_id: str, steps: str) -> bool:
    ''' Обновление задачи: добавление описания и обновление статуса'''
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по обновлению задачи')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""UPDATE tasks SET steps = %s, status=%s \
            WHERE card_id=%s""", (steps, True, card_id))
        conn.commit()

        info('db', f"Успешно обновлена задача: {card_id}")
        debug('db', 'Конец работы с БД по обновлению задачи')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при обновлении задачи: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()
import pandas as pd
import os
import psycopg2
import psycopg2.extras
from utils.logger import info, debug, err
params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

def _read_file():
    return pd.read_csv(os.getenv('PATH_TO_APP_FOLDER') + '/data/' + 'tasks.csv', sep=';')

def insert_tasks() -> bool:
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по созданию таблицы с задачами')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor()
        file = _read_file()
        for i in file.shape[0]:
            to_ = f"INSERT INTO tasks (description, steps, category_id, status) \
                VALUES ('{file.description[i]}, {file.steps[i]}, {file.category_id[i]}, {True}')"
            cursor.execute(to_)
        conn.commit()

        info('db', 'Успешно создана таблица с задачами')
        debug('db', 'Конец работы с БД по созданию таблицы с задачами')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при создании таблицы: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()
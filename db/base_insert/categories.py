import pandas as pd
import psycopg2
import psycopg2.extras
import os
from utils.logger import info, debug, err


params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

def _parse_category():
    file = pd.read_csv(os.getenv('PATH_TO_APP_FOLDER') + '/data/' + os.getenv('CATEGORIES_FILE'),
        header=None)
    return [v[0] for v in file.values]

def insert_categories() -> bool:
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по созданию таблицы с категориями')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor()
        for category in _parse_category():
            to_ = f"INSERT INTO categories (name) \
                VALUES ('{category}')"
            cursor.execute(to_)
        conn.commit()

        info('db', 'Успешно создана таблица с категорями')
        debug('db', 'Конец работы с БД по созданию таблицы с категориями')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при создании таблицы: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()
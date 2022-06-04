import pandas as pd
import os
import psycopg2
import psycopg2.extras

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
    try:
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor()
        file = _read_file()
        for i in file.shape[0]:
            to_ = f"INSERT INTO tasks (description, steps, category_id, status) \
                VALUES ('{file.description[i]}, {file.steps[i]}, {file.category_id[i]}, {True}')"
            cursor.execute(to_)
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError):
        return False
    finally:
        if conn is not None:
            conn.close()
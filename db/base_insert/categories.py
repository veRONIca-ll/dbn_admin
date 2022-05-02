import pandas as pd
import psycopg2
import psycopg2.extras
import os


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
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor()
        for category in _parse_category():
            to_ = f"INSERT INTO categories (name) \
                VALUES ('{category}')"
            cursor.execute(to_)
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
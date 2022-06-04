from bs4 import BeautifulSoup
import requests
import re
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

TAG_RE = re.compile(r'<[^>]+>')
BETWEEN_RE = re.compile(r'\((.*?)\)')
URL = os.getenv('SITE_URL')


def _get_between_brakets(text: str) -> str:
    return BETWEEN_RE.search(text).group(0)[1:-1].capitalize()

def _collect_main_deps() -> list:
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    main_deps = []

    if page.status_code != 200:
        err('db', 'Ошибка отправки запроса к сайту')
        return []

    all_rows = soup.find_all('tr')
    strong = 0
    for tr in all_rows:
        raw_department = tr.find('td').find('p')
        if raw_department and raw_department.find_all('strong') != []:
            strong += 1
        if strong == 3:
            break
        if raw_department and 'Заместитель' in raw_department.text:
            main_deps.append(_get_between_brakets(raw_department.text))
    
    return main_deps


def insert_departments() -> bool:
    global connection_param
    conn = None
    try:
        debug('db', 'Начало работы с БД по созданию таблицы с отделами')
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        list_deps = _collect_main_deps()
        if list_deps == []:
            raise Exception('No 200 status')
        for dep in _collect_main_deps():
            to_ = f"INSERT INTO departments (name) \
                VALUES ('{dep}')"
            cursor.execute(to_)
        conn.commit()

        info('db', 'Успешно создана таблица с отделами')
        debug('db', 'Конец работы с БД по созданию таблицы с отделами')
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        err('db', f'Возникла ошибка при создании таблицы: {error}')
        return False
    finally:
        if conn is not None:
            conn.close()

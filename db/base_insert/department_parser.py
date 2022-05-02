from bs4 import BeautifulSoup
import requests
import re
import psycopg2
import psycopg2.extras
import os

params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

connection_param = 'host={host} user={user} password={password}'.format(**params)

TAG_RE = re.compile(r'<[^>]+>')
BETWEEN_RE = re.compile(r'\((.*?)\)')
URL = os.getenv('SITE_URL')

def remove_tags(text: str) -> str:
    ''' Remove all html-tags from text '''
    return TAG_RE.sub('', text)

def get_between_brakets(text: str) -> str:
    return BETWEEN_RE.search(text).group(0)[1:-1].capitalize()


def collect_departments() -> list:
    ''' Collect departments from web-site into list'''
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    departments = []

    if page.status_code != 200:
        print('Sorry, cannot connect')

    all_rows = soup.find_all('tr')
    for tr in all_rows:
        raw_department = tr.find('td').find('p')
        if raw_department:
            raw_title = raw_department.find_all('strong')
            title = ''
            if raw_title == []:
                continue
            for raw_ in raw_title:
                title += remove_tags(str(raw_))
            departments.append(title)

    return departments

def _collect_main_deps() -> list:
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    main_deps = []

    if page.status_code != 200:
        print('Sorry, cannot connect')

    all_rows = soup.find_all('tr')
    strong = 0
    for tr in all_rows:
        raw_department = tr.find('td').find('p')
        if raw_department and raw_department.find_all('strong') != []:
            strong += 1
        if strong == 3:
            break
        if raw_department and 'Заместитель' in raw_department.text:
            main_deps.append(get_between_brakets(raw_department.text))
    
    return main_deps


def insert_departments() -> bool:
    global connection_param
    try:
        # TODO: add logging of starting connection
        conn = psycopg2.connect(connection_param)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        for dep in _collect_main_deps():
            to_ = f"INSERT INTO departments (name) \
                VALUES ('{dep}')"
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

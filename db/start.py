import os
import sys
# sys.path is a list of absolute path strings
sys.path.append(os.getenv('PATH_TO_APP_FOLDER'))
from install.create_table import create_tables
from base_insert.department_parser import collect_departments, insert_departments
from base_insert.categories import parse_category, insert_categories


if __name__ == '__main__':
    conn_params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }

    if create_tables(conn_params):

        ''' 
            Добавление в таблицу departments навправлений отделений,
            полученнных с сайта env.SITE_URL
        '''
        insert_departments()

        ''' 
            Добавление в таблицу categories категорий заявок,
            полученнных из файла data/categories.csv
        '''
        insert_categories()

        # TODO: база знаний по заявкам
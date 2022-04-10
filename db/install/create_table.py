import psycopg2
import os
from dotenv import load_dotenv

def create_tables(params) -> None:
    """create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE departments (
            department_id INT GENERATED ALWAYS AS IDENTITY,
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (department_id)
        )
        """,
        """
        CREATE TABLE users (
            user_id INT GENERATED ALWAYS AS IDENTITY,
            first_name VARCHAR(255) NOT NULL,
            second_name VARCHAR(255) NOT NULL,
            middle_name VARCHAR(255) NULL,
            department_id INT NOT NULL,
            PRIMARY KEY (user_id),
            CONSTRAINT fk_departments
                FOREIGN KEY(department_id) 
                    REFERENCES departments(department_id)
                        ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE staff (
            staff_id INTEGER PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            second_name VARCHAR(255) NOT NULL,
            middle_name VARCHAR(255) NULL
        )
        """,
        """
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE tasks (
            task_id INTEGER PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description VARCHAR(255) NULL,
            steps TEXT NULL,
            status BOOLEAN NOT NULL,
            category_id INTEGER NULL,
            user_id INTEGER NOT NULL,
            staff_id INTEGER NULL,
            FOREIGN KEY (category_id)
                REFERENCES categories (category_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id)
                REFERENCES users (user_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (staff_id)
                REFERENCES staff (staff_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
        )
    conn = None
    try:
        # read the connection parameters
        # connect to the PostgreSQL server
        # TODO: add logging of starting connection
        conn = psycopg2.connect("host={host} database={database} user={user} password={password}".format(**params))
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        # TODO: add logging of an error while connection
        print(error)
    finally:
        if conn is not None:
            # TODO: add logging about closing
            conn.close()


if __name__ == '__main__':
    conn_params = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
    }
    create_tables(conn_params)

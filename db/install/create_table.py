import psycopg2
import os

def create_tables(params) -> bool:
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
            user_id INT PRIMARY KEY,
            nick VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NULL,
            second_name VARCHAR(255) NULL,
            middle_name VARCHAR(255) NULL,
            department_id INT NULL,
            admin BOOLEAN,
            CONSTRAINT fk_departments
                FOREIGN KEY(department_id) 
                    REFERENCES departments(department_id)
                        ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE categories (
            category_id INT GENERATED ALWAYS AS IDENTITY,
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (category_id)
        )
        """,
        """
        CREATE TABLE tasks (
            task_id INT GENERATED ALWAYS AS IDENTITY,
            card_id VARCHAR(100) NULL,
            description TEXT NULL,
            steps TEXT NULL,
            status BOOLEAN NOT NULL,
            category_id INTEGER NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (category_id)
                REFERENCES categories (category_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id)
                REFERENCES users (user_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY (task_id)
        )
        """
        )
    conn = None
    try:
        conn = psycopg2.connect("host={host} user={user} password={password}".format(**params))
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        return False
    finally:
        if conn is not None:
            conn.close()
        


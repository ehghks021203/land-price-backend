from mysql.connector import Error
from database import create_connection, ROOT_PW, USER_NAME, USER_PW, DATABASE_NAME


def create_database(connection: object, query: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("# Database created successfully.")
    except Error as err:
        print(f'Error: "{err}"')


def create_user(connection: object, username: str, password: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';"
        )
        print("# User created successfully.")
    except Error as err:
        print(f'Error: "{err}"')


def grant_privileges(connection: object, username: str, database: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON {database}.* TO '{username}'@'localhost';"
        )
        connection.commit()
        print("# Privileges granted successfully.")
    except Error as err:
        print(f'Error: "{err}"')


def make() -> None:
    print("localhost", "root", ROOT_PW)
    connection = create_connection("localhost", "root", ROOT_PW)
    create_database(connection, f"CREATE DATABASE {DATABASE_NAME}")
    create_user(connection, USER_NAME, USER_PW)
    grant_privileges(connection, USER_NAME, DATABASE_NAME)

    if connection:
        connection.close()
        print("# MySQL connection is closed.")

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/kumap/land-price-backend/.env")

ROOT_PW = os.getenv("ROOT_PW")
DATABASE_NAME = os.getenv("DATABASE_NAME")
USER_NAME = os.getenv("USER_NAME")
USER_PW = os.getenv("USER_PW")


def create_connection(
    host_name: str, user_name: str, user_password: str, database: str = None
) -> object:
    connection = None
    try:
        if database:
            connection = mysql.connector.connect(
                host=host_name, user=user_name, passwd=user_password, database=database
            )
        else:
            connection = mysql.connector.connect(
                host=host_name, user=user_name, passwd=user_password
            )
        print("# MySQL Database connection successful.")
    except Error as err:
        print(f'Error: "{err}"')
    return connection

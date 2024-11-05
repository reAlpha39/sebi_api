import mysql.connector
from mysql.connector import Error
from config import settings


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            passwd=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
    except Error as e:
        raise e

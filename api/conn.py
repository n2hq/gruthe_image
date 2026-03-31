from flask_mysqldb import MySQL
import pymysql
from .config import DB_CONFIG


def get_connection():
    connection = pymysql.connect(**DB_CONFIG,
                             cursorclass=pymysql.cursors.DictCursor)
    return connection
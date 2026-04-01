from flask_mysqldb import MySQL
import pymysql
import os
from init import app
from init import DB_CONFIG

def get_connection():
    

    connection = pymysql.connect(**DB_CONFIG,
                             cursorclass=pymysql.cursors.DictCursor)
    return connection
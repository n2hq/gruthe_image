import os
from init import app

env = os.getenv("APP_ENV", "dev")

DBHOST = os.getenv("HOST")
DBPASS = os.getenv("PASSWORD")
DBUSER = os.getenv("USER")
DBBASE = os.getenv("DATABASE")

DB_CONFIG = {
    "host": "localhost",  # or "localhost"
    "user": "root",       # Default XAMPP user
    "password": "",       # Leave empty if no password is set
    "database": "dbdir",
}
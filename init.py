from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

env = os.getenv("APP_ENV", "dev")
load_dotenv(f".env.{env}")


app = Flask(__name__)

app.config['media'] = '../vmedia'
app.config['allowed_extensions'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}


DBHOST = os.getenv("DBHOST")
DBPASS = os.getenv("DBPASS")
DBUSER = os.getenv("DBUSER")
DBBASE = os.getenv("DBBASE")

print(f"{DBUSER}")
DB_CONFIG = {
        "host": DBHOST,  # or "localhost"
        "user": DBUSER,       # Default XAMPP user
        "password": DBPASS,      
        "database": DBBASE,
    }

CORS(app)
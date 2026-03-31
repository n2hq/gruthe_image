from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

app.config['media'] = '../vmedia'
app.config['allowed_extensions'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}

CORS(app)
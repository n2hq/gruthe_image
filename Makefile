dev:
	APP_ENV=dev python app.py

start:
	APP_ENV=prod gunicorn --bind 127.0.0.1:8885 run:app

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt
from flask import Flask
from rgr import rgr

from Db import db 
from Db.models import users 
from flask_login import LoginManager


app=Flask(__name__)

app.secret_key = "12345"
user_db = "ZaikoPolinaRGR"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "RGR_Books"
password = "12345"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# директория для загруженных файлов
UPLOAD_FOLDER = './static/oblozhki'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Подключаем Flask-Login
login_manager = LoginManager()
# Куда редиректить, если пользователь не авторизован, # а он пытается попасть на защищенную страницу
login_manager.login_view = "rgr.login"
login_manager.init_app(app)
# Показываем Flask-Login как и где найти нужного пользователя
@login_manager.user_loader
def load_users(user_id):
    # Метод get вернет объект users с нужным id 
    #со всеми атрибутами и методами класса
    return users.query.get(int(user_id))

app.register_blueprint(rgr)

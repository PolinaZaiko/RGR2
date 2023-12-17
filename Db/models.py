# импортируем переменную db из файла
from . import db 
from flask_login import UserMixin

'''
Описываем схему нашей БД в виде объектов
Таким образом, создание таблиц (схемы БД) возьмет 
на себя SQLAlchemy - система ORM.
'''

class users(db.Model, UserMixin):
    id = db.Column (db. Integer, primary_key=True)
    username = db.Column (db.String(30), nullable=False, unique=True)
    password = db.Column (db.String(102), nullable=False)

    # repr - от слова represent
    # мы подсказываем ORM как отображать эти 
    # # данные в строковом виде
    
    def __repr__ (self):
        return f'id: {self.id}, username: {self.username}'

class books(db.Model):
    id = db.Column (db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(500)) #поле обложки

    def repr (self):
        return f'title: {self.title}, author: {self.author}, pages: {self.pages}, publisher:{self.publisher}, cover:{self.cover}'
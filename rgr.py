from flask import Blueprint, abort, request, render_template, redirect
from Db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from Db.models import users, books
import psycopg2

rgr = Blueprint ("rgr", __name__)

@rgr.route("/")
@rgr.route("/index")
def start():
    return redirect ("/rgr", code=302)

@rgr.route ("/rgr")
def main():
    return render_template('rgr.html')

@rgr.route ("/rgr")
def aut():
    username = current_user.username
    return render_template('rgr.html', username=username)

@rgr.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/rgr')


@rgr.route("/rgr/register", methods=["GET", "POST"]) 
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username_form = request.form.get("username")
    password_form = request.form.get("password")

    #Проверка на пустое имя
    if not username_form:
        return render_template("register.html", error="Пустое имя")

    # Проверка на длину пароля
    if len(password_form) < 8:
        return render_template("register.html", error="Пароль меньше 8-ти символов")

    '''
    Проверяем существование пользователя в БД с таким же именем
    Если такого пользователя нет, то в isUserExist вернется None 
    т.е. мы можем интерпретировать это как False
    '''

    '''
    select * from users
    WHERE username = username form
    LIMIT 1
    -- где username_form - это имя, которое мы получили из формы
    '''

    isUserExist = users.query.filter_by(username=username_form).first()

    # Проверка на существование пользователя
    if isUserExist is not None:
        return render_template ("register.html", error="Пользователь с таким именем уже существует")
    
    # Хэшируем пароль
    hashedPswd = generate_password_hash(password_form, method='pbkdf2')
    # Создаем объект users с нужными полями
    newUser = users(username=username_form, password=hashedPswd)
    # Это INSERT
    db.session.add(newUser)

    # Тоже самое, что и conn.commit ()
    db.session.commit ()

    # Перенаправляем на страницу логина
    return redirect("/rgr/login")

@rgr.route ("/rgr/login", methods= ["GET", "POST"]) 
def login():
    if request.method == "GET":
        return render_template ("login.html")
        
    username_form = request.form. get ("username")
    password_form = request. form.get ("password")

    #Проверка на пустое имя
    if not username_form:
        return render_template("login.html", error="Пустое имя")

    #Проверка на пустой пароль
    if not password_form:
        return render_template("login.html", error="Пустой пароль")

    my_user = users.query.filter_by(username=username_form).first()

    # Проверка на существование пользователя
    if my_user is None:
        return render_template("login.html", error="Пользователь не найден")

    # Проверка на правильность пароля
    if not check_password_hash(my_user.password, password_form):
        return render_template("login.html", error="Неправильный пароль")

    # Сохраняем JWT токен
    login_user(my_user, remember=False)
    return redirect("/rgr")


# @rgr.route ('/rgr/api', methods = ['POST'])
# def api():
#     data = request.json

#     if data [''] == '':
#         return  (data[''])
    
#     if data[''] == '':
#         return  (data [''])
    
#     if data[''] == '':
#         return (data[''])
    
#     abort (400)

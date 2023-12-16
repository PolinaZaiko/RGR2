from flask import Blueprint, request, render_template, redirect, url_for, current_app

from Db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from Db.models import users, books
import os
from werkzeug.utils import secure_filename
import time




rgr = Blueprint ("rgr", __name__)

@rgr.route("/")
@rgr.route("/index")
def start():
    return redirect ("/rgr", code=302)

@rgr.route ("/rgr")
def main():
    if current_user.is_authenticated:
        return render_template('rgr.html', username=current_user.username)
    else:
        return render_template('rgr.html')


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

# Вероятно, проблема связана с тем, как вы сохраняете файл обложки. Вы используете функцию secure_filename, которая удаляет все "небезопасные" символы из имени файла. Это может включать в себя пробелы, специальные символы и даже некоторые буквы, в зависимости от настроек вашей системы. В результате, если имя файла содержит только "небезопасные" символы, после применения secure_filename останется только расширение файла.

# Чтобы решить эту проблему, вы можете добавить к имени файла некоторую уникальную строку перед сохранением. Например, вы можете использовать текущее время или идентификатор пользователя:

@rgr.route("/rgr/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    #проверка на администратора
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        pages = request.form.get("pages")
        publisher = request.form.get("publisher")
        cover = request.files.get("cover")
        if title and author and pages and publisher and cover:
            filename = secure_filename(str(time.time()) + "_" + cover.filename)
            cover.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_book = books(title=title, author=author, pages=pages, publisher=publisher, cover=filename)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('rgr.list'))
        else:
            return render_template("add_book.html", error="Заполните все поля!")
    return render_template("add_book.html")


@rgr.route("/rgr/list", methods=["GET"])
def list():
    page = request.args.get('page', 1, type=int)

    # получаем параметры фильтрации и сортировки из запроса
    title = request.args.get("title")
    author = request.args.get("author")
    pages_from = request.args.get("pages_from")
    pages_to = request.args.get("pages_to")
    publisher = request.args.get("publisher")
    sort_by = request.args.get("sort_by")

    # начинаем с всех книг
    bookes_query = books.query

    # фильтруем по введенным данным
    if title:
        bookes_query = bookes_query.filter(books.title.contains(title))
    if author:
        bookes_query = bookes_query.filter(books.author.contains(author))
    if pages_from:
        bookes_query = bookes_query.filter(books.pages >= int(pages_from))
    if pages_to:
        bookes_query = bookes_query.filter(books.pages <= int(pages_to))
    if publisher:
        bookes_query = bookes_query.filter(books.publisher.contains(publisher))

    # сортируем по выбранному полю
    if sort_by:
        bookes_query = bookes_query.order_by(getattr(books, sort_by))

    # получаем все книги после фильтрации и сортировки
    pagination = bookes_query.paginate(page=page, per_page=20, error_out=False)
    bookes = pagination.items

    # получаем уникальные авторы, названия и издательства
    authors = books.query.with_entities(books.author).distinct().all()
    titles = books.query.with_entities(books.title).distinct().all()
    publishers = books.query.with_entities(books.publisher).distinct().all()

    return render_template('list.html', pagination=pagination, bookes=bookes, authors=authors, titles=titles, publishers=publishers)



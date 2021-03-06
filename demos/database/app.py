# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import ast
import os
import sys

import click
from flask import Flask, request, jsonify
from flask import redirect, url_for, abort, render_template, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.jinja_env.trim_blocks = True

app.jinja_env.lstrip_blocks = True

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# 数据迁移流程
# 1, 创建一个迁移环境：flask db init
# 2, 生成迁移脚本：flask db migrate -m "commit"
# 3, 更新数据库： flask db upgrade; 如果想回滚版本 : flask db downgrade 2dde5ddbf956
migrate = Migrate(app,db)


# handlers
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Note=Note, Author=Author, Article=Article, Writer=Writer, Book=Book,
                Singer=Singer, Song=Song, Citizen=Citizen, City=City, Capital=Capital,
                Country=Country, Teacher=Teacher, Student=Student, Post=Post, Comment=Comment, Draft=Draft)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# Forms
class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')


# Models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    # optional
    def __repr__(self):
        return '<Note %r>' % self.body


@app.route('/')
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    print("index 1111",notes)
    # print(Note.query.filter(Note.body.like("%111111%")).first())
    # notes = Note.query.filter(Note.body.like("%111111%")).all()
    # print("index ===",notes)
    return render_template('index.html', notes=notes, form=form)


@app.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        print("======",note.id,"========")
        return redirect(url_for('index'))
    return render_template('new_note.html', form=form)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('Your note is updated.')
        return redirect(url_for('index'))
    form.body.data = note.body  # preset form input's value
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('Your note is deleted.')
    else:
        abort(400)
    return redirect(url_for('index'))





# one to many
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20))
    articles = db.relationship('Article')  # collection

    def __repr__(self):
        return '<Author %r>' % self.name

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return '<Article %r>' % self.title

# test
@app.route('/add/<string:author>',methods=['POST'])
def add_author(author):
    articles = request.args.get('articles')
    author = Author(name=author)
    db.session.add(author)
    db.session.commit()
    for article_name in ast.literal_eval(articles):
        article = Article(title=article_name,author_id=author.id)
        db.session.add(article)
    db.session.commit()
    return 'add author with articles ok'


@app.route('/get_articles/<string:author_name>',methods=['GET'])
def get_articles(author_name):
    articles = Article.query.filter(Author.name==author_name).all()
    all_ats = ''
    for article in articles:
        all_ats = all_ats + article.title + '\n'
    return all_ats

# 验证单项查询有效
@app.route('/get_author/<string:article_name>',methods=['GET'])
def get_author(article_name):
    author = Author.query.filter(Article.title==article_name).all()
    return author[0].name

# many to one
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')  # scalar

    def __repr__(self):
        return '<Citizen %r>' % self.name


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return '<City %r>' % self.name

@app.route('/add_city_citizen/<string:city_name>',methods=['POST'])
def add_city_citizen(city_name):
    city = City(name=city_name)
    db.session.add(city)
    db.session.commit()
    citizens = request.args.get('citizens')
    for citizen in ast.literal_eval(citizens):
        city_ren = Citizen(name=citizen,city=city)
        db.session.add(city_ren)
    db.session.commit()
    return "add city and citizen ok"

@app.route('/get_citizen/<string:city_name>',methods=['GET'])
def get_citizen(city_name):
    citizen = Citizen.query.filter(City.name==city_name).all()
    print(citizen)
    mcitizen = {}
    for ct in citizen:
        mcitizen[ct.id] = ct.name
    return mcitizen

# one to one
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    capital = db.relationship('Capital', back_populates='country', uselist=False)  # collection -> scalar

    def __repr__(self):
        return '<Country %r>' % self.name


class Capital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country', back_populates='capital')  # scalar

    def __repr__(self):
        return '<Capital %r>' % self.name


@app.route('/add_country_capital',methods=['POST'])
def add_country_capital():
    country = request.args.get('country')
    capital = request.args.get('capital')
    c1 = Country(name=country)
    c2 = Capital(name=capital)
    c1.capital = c2
    db.session.add(c1)
    db.session.add(c2)
    db.session.commit()
    return country + ':' + capital

@app.route('/get_capital/<string:country_name>')
def get_capital(country_name):
    country = Country.query.filter(Country.name==country_name).first()
    capital = Capital.query.get(country.id)
    return capital.name


# many to many with association table
association_table = db.Table('association',
                             db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                             db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'))
                             )


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    age = db.Column(db.Integer)
    teachers = db.relationship('Teacher',
                               secondary=association_table,
                               back_populates='students')  # collection

    def __repr__(self):
        return '<Student %r>' % self.name


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    students = db.relationship('Student',
                               secondary=association_table,
                               back_populates='teachers')  # collection

    def __repr__(self):
        return '<Teacher %r>' % self.name

@app.route('/add_students_for_teacher/<string:teacher_name>',methods=['POST'])
def add_students_for_teacher(teacher_name):
    teacher = Teacher.query.filter(Teacher.name==teacher_name).first()
    print(teacher)
    # 如果没有teacher，加入
    if not teacher:
        teacher = Teacher(name=teacher_name,office='of')
        db.session.add(teacher)
        db.session.commit()
    students = request.args.get('students')
    # 加入students
    for student_name in ast.literal_eval(students):
        student = Student(name=student_name,grade='class1')
        if not student:
            db.session.add(student)
        # 添加关联
        teacher.students.append(student)
    db.session.commit()
    return 'add students for a teacher'

@app.route('/add_teachers_for_student',methods=['POST'])
def add_teachers_for_student():
    # student = request.get_data()
    # print(student)
    # student_name = request.form['name']
    # student_grade = request.form['grade']
    # Params
    student_name = request.args.get('name')
    student_grade = request.args.get('grade')
    student = Student(name=student_name,grade=student_grade)
    if not student:
        db.session.add(student)
        db.session.commit()
    # 添加多个老师(Body)
    teachers = request.get_data()
    print(teachers)
    mtd = eval(str(teachers, encoding="utf-8"))
    print(mtd)
    for teacher_name,office in mtd.items():
        teacher = Teacher(name=teacher_name,office=office)
        db.session.add(teacher)
        student.teachers.append(teacher)
    db.session.commit()
    return "add teachers for student ok"

# 查询
@app.route('/get_students_for_teacher/<string:teacher_name>',methods=['GET'])
def get_students_for_teacher(teacher_name):
    teacher = Teacher.query.filter(Teacher.name==teacher_name).first()
    st = {}
    if not teacher:
        return "没查到这个老师"
    for student in teacher.students:
        st[student.name] = student.grade
    return st

@app.route('/get_teachers_for_student/<string:student_name>',methods=['GET'])
def get_teachers_for_student(student_name):
    student = Student.query.filter(Student.name==student_name).first()
    tr = {}
    if not student:
        return "没有这个学生"
    for teacher in student.teachers:
        tr[teacher.name] = teacher.office
    return tr

# one to many + bidirectional relationship
class Writer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    books = db.relationship('Book', back_populates='writer')

    def __repr__(self):
        return '<Writer %r>' % self.name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')

    def __repr__(self):
        return '<Book %r>' % self.name

@app.route('/add_writer/<string:writer>',methods=['POST'])
def add_writer(writer):
    king = Writer(name=writer)
    db.session.add(king)
    db.session.commit()
    books = request.args.get('books')
    print(king.books)
    for book_name in ast.literal_eval(books):
        book = Book(name=book_name)
        # 方式1
        # book.writer = king
        # 方式2
        king.books.append(book)
        db.session.add(book)
    db.session.commit()
    return 'add writer and books ok'


# one to many + bidirectional relationship + use backref to declare bidirectional relationship
class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    songs = db.relationship('Song', backref='singer')

    def __repr__(self):
        return '<Singer %r>' % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singer.id'))

    def __repr__(self):
        return '<Song %r>' % self.name


@app.route('/add_song/<string:singer_name>',methods=['POST'])
def add_song(singer_name):
    singer = Singer(name=singer_name)
    db.session.add(singer)
    db.session.commit()
    songs = request.args.get('songs')
    song = Song(name=songs,singer_id=singer.id)
    db.session.add(song)
    db.session.commit()
    return 'add sing and song ok!'


# cascade
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')  # collection


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    body = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')  # scalar

@app.route('/add_comments_for_post',methods=['POST'])
def add_comments_for_post():
    # Params
    title_name = request.args.get('title')
    body_name = request.args.get('body')
    # 实例化Post
    post = Post(title=title_name,body=body_name)
    if not post:
        db.session.add(post)
        db.session.commit()
    # 获取所有comment
    data = request.data
    print(data)
    comments = eval(str(data,encoding='utf-8'))
    for author,body in comments.items():
        comment = Comment(author=author,body=body,post_id=post.id)
        db.session.add(comment)
        post.comments.append(comment)
    db.session.commit()
    return 'add all comments for post ok'

# 删除文章，级联删除评论
@app.route('/delete_post/<string:title_name>',methods=['DELETE'])
def delete_post(title_name):
    post = Post.query.filter(Post.title==title_name).first()
    # post = Post.query.get(1)
    if post:
        db.session.delete(post)
        db.session.commit()
        return "delete post and relation comments"
    return "没有这样的标题文章"

# 删除评论
@app.route('/delete_comment/<string:title_name>/<string:comment_name>',methods=['DELETE'])
def delete_comment(title_name,comment_name):
    post = Post.query.filter(Post.title==title_name).first()
    comments = Comment.query.filter(Comment.author==comment_name).all()
    for comment in comments:
        post.comments.remove(comment)
    db.session.commit()
    return "单独解除post和comment的关系"

# event listening
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    edit_time = db.Column(db.Integer, default=0)


@db.event.listens_for(Draft.body, 'set')
def increment_edit_time(target, value, oldvalue, initiator):
    # if value==0:
    #     target.edit_time = 0
    if value:
        target.edit_time += 1

# 测试listen
@app.route('/event_listen/<int:value>',methods=['POST'])
def event_listen(value):
    draft = Draft(body=value)
    db.session.add(draft)
    db.session.commit()
    return str(draft.edit_time)

@app.route('/body_monitor/<string:body>',methods=['POST'])
def body_monitor(body):
    draft = Draft.query.filter(Draft.body==body).first()
    draft.body = body
    if isinstance(draft.body,int):
        return str(draft.body)
    db.session.commit()
    return draft.body

@app.route('/get_edit_time/<string:body>',methods=['GET'])
def get_edit_time(body):
    draft = Draft.query.filter(Draft.body==body).first()
    return str(draft.edit_time)


# same with:
# @db.event.listens_for(Draft.body, 'set', named=True)
# def increment_edit_time(**kwargs):
#     if kwargs['target'].edit_time is not None:
#         kwargs['target'].edit_time += 1


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)

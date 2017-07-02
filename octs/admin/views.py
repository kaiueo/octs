from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course, User, Permission
from .forms import CourseForm, TermForm, MemberForm
from octs.user.models import Term
from octs.database import db
import time
import datetime
import os
import xlrd
# -*- coding: UTF-8 -*-
blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')
@blueprint.route('/term')
def term():
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    time_now = datetime.date.fromtimestamp(time.time())
    return render_template('admin/term.html', list=termList, endtime=termList[0],nowtime=time_now)
@blueprint.route('/term/add',methods=['GET','POST'])
def term_add():
    form=TermForm()
    if form.validate_on_submit():
        name = form.termname.data
        weeknum = form.week_number.data
        term = Term(name=name, week_number=weeknum)
        term.start_time=form.start_time.data
        term.end_time=form.end_time.data
        db.session.add(term)
        db.session.commit()
        return redirect(url_for('admin.home'))
    return render_template('admin/term/add.html',form=form)

@blueprint.route('/course')
def course():
    courseList = Course.query.all()
    return render_template('admin/course.html', list=courseList)

@blueprint.route('/mainpage')
def home():
    return render_template('admin/mainpage.html')

@blueprint.route('/course/add',methods=['GET','POST'])
def insert():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(form.coursename.data)
        ##course.name = form.coursename.data
        course.credit = form.credit.data
        course.location = form.location.data
        course.course_introduction = form.course_introduction.data
        course.start_time = form.start_time.data
        course.term_id = 1
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.course'))
    return render_template('admin/add.html',form=form)

@blueprint.route('/course/edit/<id>',methods=['GET','POST'])
def edit(id):
    form = CourseForm()

    course = Course.query.filter_by(id = id).first()

    if form.validate_on_submit():
        course.name = form.coursename.data
        course.credit = form.credit.data
        course.location = form.location.data
        course.course_introduction = form.course_introduction.data
        course.start_time = form.start_time.data
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.course'))
    form.coursename.data = course.name
    form.credit.data = course.credit
    form.location.data = course.location
    form.course_introduction.data = course.course_introduction
    form.start_time.data = course.start_time


    return render_template('admin/edit.html',form=form)

@blueprint.route('/course/delete/<id>')
def delete(id):
    course = Course.query.filter_by(id = id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin.course'))

@blueprint.route('/course/member/<id>')
def member(id):
    course = Course.query.filter_by(id=id).first()
    userList = course.users
    return render_template('admin/member.html', list=userList, courseid=id)

def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))

def excel_table_byindex(file='file.xls', colnameindex=0, by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    colnames = table.row_values(colnameindex)  # 某一行数据
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            list.append(app)
    return list

@blueprint.route('/course/member/add/<id>' ,methods=['GET','POST'])
def add_member(id):
    form = MemberForm()
    if form.validate_on_submit():
        file = form.file.data
        filepath = os.path.join(os.getcwd(), 'uploads', file.filename)
        file.save(filepath)
        tables = excel_table_byindex(file=filepath, by_index=0)
        course = Course.query.filter_by(id=id).first()
        for row in tables:
            user_id = row['user_id']
            name = row['name']
            gender = row['gender']
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                user = User(username=user_id, permission=Permission.STUDENT, password='111')
                user.name = name
                user.gender = gender
                user.user_id = user_id
            if user not in course.users:
                course.users.append(user)
            db.session.add(user)

        tables = excel_table_byindex(file=filepath, by_index=1)
        for row in tables:
            user_id = row['user_id']
            name = row['name']
            gender = row['gender']
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                user = User(username=user_id, permission=Permission.TEACHER, password='111')
                user.name = name
                user.gender = gender
                user.user_id = user_id
            if user not in course.users:
                course.users.append(user)
            db.session.add(user)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.member', id=id))

    return render_template('admin/addMember.html', form=form, courseid=id)

@blueprint.route('/course/<course_id>/member/delete/<user_id>')
def delete_member(course_id, user_id):
    course = Course.query.filter_by(id=course_id).first()
    user = User.query.filter_by(id=user_id).first()
    course.users.remove(user)
    db.session.add(course)
    db.session.commit()
    return redirect(url_for('admin.member', id=course_id))




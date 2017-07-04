from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course, User, Permission
from .forms import CourseForm, TermForm, MemberForm
from octs.user.models import Term, Tag,UserScore
from octs.database import db
import time
import datetime
import os
import xlrd
import re
# -*- coding: UTF-8 -*-
blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')
@blueprint.route('/term')
def term():
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    time_now = datetime.date.fromtimestamp(time.time())
    return render_template('admin/term.html', list=termList,nowtime=time_now)
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
    nowtime = datetime.date.fromtimestamp(time.time())
    term = Term.query.order_by(Term.id.desc()).first()
    return render_template('admin/course.html', list=courseList, nowtime=nowtime, term=term)

@blueprint.route('/mainpage')
def home():
    return render_template('admin/mainpage.html')

@blueprint.route('/course/add',methods=['GET','POST'])
def insert():
    courseList = Course.query.all()
    form = CourseForm()
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    nowtime = datetime.date.fromtimestamp(time.time())
    term = Term.query.order_by(Term.id.desc()).first()
    #flash(''+str(nowtime) + ' ' +str(termList[0].end_time))
    if  termList[0].end_time <= nowtime:
        flash('学期已结束，不可添加课程！')
        return render_template('admin/course.html', list=courseList,term=term,nowtime=nowtime)
    else :
            if form.validate_on_submit():
                course = Course(form.coursename.data)
                ##course.name = form.coursename.data
                course.credit = form.credit.data
                course.location = form.location.data
                course.course_introduction = form.course_introduction.data
                course.start_time = form.start_time.data
                course.end_time = form.end_time.data
                term = Term.query.order_by(Term.id.desc()).first()
                course.term = term
                tag = Tag()
                tag.name = '默认'
                course.tags.append(tag)
                if termList[0].start_time > course.start_time or termList[0].end_time < course.end_time or course.end_time < course.start_time:
                    flash('课程时间错误！')
                    return redirect(url_for('admin.insert'))
                else:
                    db.session.add(course)
                    db.session.add(tag)
                    db.session.commit()
                    return redirect(url_for('admin.course'))
            return render_template('admin/add.html',form=form)

@blueprint.route('/course/edit/<id>',methods=['GET','POST'])
def edit(id):
    course = Course.query.filter_by(id = id).first()
    form = CourseForm()
    term = Term.query.order_by(Term.id.desc()).first()
    courseList = Course.query.all()
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    nowtime = datetime.date.fromtimestamp(time.time())
    if course.term_id < term.id :
        flash('该课程为往期课程，不可编辑！')
        return render_template('admin/course.html', list=courseList, term = term , nowtime = nowtime)
    else:
        if form.validate_on_submit():
            course.name = form.coursename.data
            course.credit = form.credit.data
            course.location = form.location.data
            course.course_introduction = form.course_introduction.data
            course.start_time = form.start_time.data
            course.end_time = form.end_time.data
            if termList[0].start_time > course.start_time or termList[0].end_time < course.end_time or course.end_time < course.start_time:
                flash('课程时间错误！')
                return redirect(url_for('admin.edit',id=id))
            else:
                db.session.add(course)
                db.session.commit()
                return redirect(url_for('admin.course'))
        form.coursename.data = course.name
        form.credit.data = course.credit
        form.location.data = course.location
        form.course_introduction.data = course.course_introduction
        form.start_time.data = course.start_time
        form.end_time.data = course.end_time

        return render_template('admin/edit.html', form=form)

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

def isnumber(num):
    regex = re.compile(r"^(-?\d+)(\.\d*)?$")
    if re.match(regex,num):
        return True
    else:
        return False

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
            if isnumber(str(row['user_id'])):
                row_user_id = str(int(row['user_id']))
            else:
                row_user_id = str(row['user_id'])

            user_id = row_user_id
            name = row['name']
            gender = row['gender']
            if gender=='男':
                gender=False
            else:
                gender=True
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                user = User(username=user_id, permission=Permission.STUDENT, password='111')
                user.name = name
                user.gender = gender
                user.user_id = user_id
            if user not in course.users:
                userscore = UserScore()
                userscore.user_id = user.id
                db.session.add(userscore)
                course.users.append(user)
            db.session.add(user)

        tables = excel_table_byindex(file=filepath, by_index=1)
        for row in tables:
            if isnumber(str(row['user_id'])):
                row_user_id = str(int(row['user_id']))
            else:
                row_user_id = str(row['user_id'])

            user_id = row_user_id
            name = row['name']
            gender = row['gender']
            if gender=='男':
                gender=False
            else:
                gender=True
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




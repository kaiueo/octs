from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from octs.user.models import Course
from .forms import CourseForm
from octs.database import db

blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('admin/index.html')

@blueprint.route('/course')
def course():
    courseList = Course.query.all()
    return render_template('admin/course.html', list=courseList)

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

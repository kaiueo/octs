from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course,Task, User
from .forms import CourseForm,TaskForm
from octs.database import db
from flask_login import current_user

blueprint = Blueprint('teacher', __name__, url_prefix='/teacher',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('teacher/index.html')


@blueprint.route('/<teacherid>/course/')
def course(teacherid):
    teacher = User.query.filter_by(id=teacherid).first()
    courseList = teacher.courses
    return render_template('teacher/course.html', list=courseList)


@blueprint.route('/<teacherid>/course/edit/<id>',methods=['GET','POST'])
def course_edit(teacherid, id):
    course = Course.query.filter_by(id=id).first()
    form = CourseForm()
    if form.validate_on_submit():
        course.course_introduction = form.course_introduction.data
        course.course_outline=form.course_outline.data
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher.course', teacherid=teacherid))

    form.coursename.data=course.name
    form.credit.data=course.credit
    form.location.data=course.location
    form.start_time.data=course.start_time
    form.course_introduction.data=course.course_introduction
    form.course_outline.data=course.course_outline



    return render_template('teacher/course_edit.html',form=form)



@blueprint.route('/course/student/<id>')
def student(id):
    course=Course.query.filter_by(id=id).first()
    studentList = course.users
    return render_template('teacher/student.html',list=studentList)

@blueprint.route('/mainpage/')
def mainpage():
    return render_template('teacher/mainpage.html')

@blueprint.route('/<courseid>/task')
def task(courseid):
    taskList = Task.query.filter_by(course_id=courseid).all()
    return render_template('teacher/task.html',list = taskList, courseid=courseid)

@blueprint.route('/<courseid>/task/add',methods = ['GET','POST'])
def add(courseid):
    form = TaskForm()
    if form.validate_on_submit():
        task = Task()
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.teacher = current_user.name
        task.course_id = form.content.data
        course = Course.query.filter_by(id=courseid).first()
        course.tasks.append(task)
        db.session.add(task)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher.task', courseid=courseid))
    return render_template('teacher/add.html',form=form, courseid=courseid)

@blueprint.route('/<courseid>/task/edit/<id>',methods = ['GET','POST'])
def task_edit(courseid, id):
    form = TaskForm()
    task = Task.query.filter_by(id = id).first()
    if form.validate_on_submit():
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.content = form.content.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('teacher.task', courseid=courseid))

    form.taskname.data = task.name
    form.starttime.data = task.start_time
    form.endtime.data = task.end_time
    form.content.data = task.content
    return render_template('teacher/edit.html',form = form, courseid=courseid)

@blueprint.route('/<courseid>/task/delete/<id>')
def delete(courseid, id):
    task = Task.query.filter_by(id = id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('teacher.task', courseid=courseid))





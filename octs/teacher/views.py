from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course
from .forms import CourseForm
from octs.database import db

blueprint = Blueprint('teacher', __name__, url_prefix='/teacher',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('teacher/index.html')


@blueprint.route('/course/')
def course():
    courseList = Course.query.all()
    return render_template('teacher/course.html', list=courseList)


@blueprint.route('/course/edit/<id>',methods=['GET','POST'])
def course_edit(id):
    course = Course.query.filter_by(id=id).first()
    form = CourseForm()
    if form.validate_on_submit():
        course.course_introduction = form.course_introduction.data
        course.course_outline=form.course_outline.data
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher.course'))

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



from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course

blueprint = Blueprint('teacher', __name__, url_prefix='/teacher',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('teacher/index.html')


@blueprint.route('/course/')
def course():
    courseList = Course.query.all()
    return render_template('teacher/course.html', list=courseList)


@blueprint.route('/course/edit/<id>')
def course_edit(id):
    course = Course.query.filter_by(id=id).first()

    return render_template('teacher/course_edit.html',course=course)


@blueprint.route('/course/student/<id>')
def student(id):
    course=Course.query.filter_by(id=id).first()
    studentList = course.users
    return render_template('teacher/student.html',list=studentList)


from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course
from .forms import CourseForm

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

    return render_template('admin/add.html',form=form)

@blueprint.route('/course/edit/<id>')
def edit(id):
    return render_template('admin/edit.html',id=id)

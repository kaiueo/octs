from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.database import Column, Model, SurrogatePK, db, reference_col, relationship
from octs.user.models import Course
from .forms import CourseForm
from .forms import TermForm
from octs.user.models import Term
import time
import datetime

blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('admin/index.html')
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

@blueprint.route('/course/add',methods=['GET','POST'])
def insert():
    form = CourseForm()
    return render_template('admin/add.html',form=form)

@blueprint.route('/course/edit/<id>')
def edit(id):
    return render_template('admin/edit.html',id=id)

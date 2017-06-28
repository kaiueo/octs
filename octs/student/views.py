from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course,Term,Team
from .forms import CourseForm
from octs.database import db
import time
import datetime


blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('student/index.html')

@blueprint.route('/course/')
def course():
    courseList = Course.query.all()
    return render_template('student/course.html', list=courseList)


@blueprint.route('/checkterm/')
def checkterm():
    termList = Term.query.all()
    time_now = datetime.date.fromtimestamp(time.time())
    return render_template('student/checkterm.html', list=termList,endtime=termList[0],nowtime=time_now)

@blueprint.route('/mainpage/')
def mainpage():
    return render_template('student/mainpage.html')

@blueprint.route('/team')
def team():
    teamlist=Team.query.all()
    return render_template('student/team.html',list=teamlist)
@blueprint.route('/team/create')
def create_team():
    return render_template('student/team/create.html')
@blueprint.route('/team/myTeam')
def my_team():
    return render_template('student/team/myTeam.html')

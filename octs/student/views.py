from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import User,Course,Term,Team,TeamUserRelation
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
    return render_template('student/team.html')


@blueprint.route('/team/create')
def create_team():
    return render_template('student/team/create.html')


@blueprint.route('/team/<id>')
def my_team(id):
    t1 = TeamUserRelation.query.filter_by(user_id=id).first()
    flag = 1
    if t1 :
        teamid = t1.team_id
        tars = TeamUserRelation.query.filter(TeamUserRelation.team_id == teamid).filter(TeamUserRelation.is_accepted == True).all()
        print(tars)
        userList = [tar.user for tar in tars]
        myteam = Team.query.filter_by(id=teamid).first()
        return render_template('student/team/myTeam.html',myteam=myteam,flag=flag,userList=userList)
    else:
        flag = 0
        return render_template('student/team/myTeam.html',flag=flag)

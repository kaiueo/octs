from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course,Term,Team,TeamUserRelation,User
from .forms import CourseForm
from octs.database import db
import time
import datetime
from octs.student.forms import TeamRequireForm


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

@blueprint.route('/team',methods=['GET', 'POST'])
def team():
    form=TeamRequireForm()
    teamlist=Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(
    TeamUserRelation.team_id==Team.id).filter(TeamUserRelation.is_master==True).join(
    User,TeamUserRelation.user_id==User.id).filter(TeamUserRelation.user_id==User.id).add_columns(
    Team.name,User.username,Team.status,Team.id,User.user_id,User.in_team)

    return render_template('student/team.html',list=teamlist,form=form)
@blueprint.route('/team/create')
def create_team():
    return render_template('student/team/create.html')
@blueprint.route('/team/myTeam')
def my_team():
    return render_template('student/team/myTeam.html')

@blueprint.route('/team/<teamid>/add/<userid>',methods=['GET', 'POST'])
def add_team(teamid, userid):
    userRela=User.query.filter_by(id=userid).first()
    teamRela=TeamUserRelation()
    teamRela.user_id=userid
    teamRela.team_id=teamid
    teamRela.is_master=False
    teamRela.is_accepted=False
    db.session.add(teamRela)
  
    userRela.in_team=True
    db.session.add(userRela)
    db.session.commit()
    return render_template('student/team/myTeam.html')
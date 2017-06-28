from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course,Term,Team,TeamUserRelation,User
from .forms import TeamForm
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
@blueprint.route('/team/create/<id>',methods=['GET','POST'])
def create_team(id):
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        team.name = form.teamname.data
        team.status = 0
        db.session.add(team)
        db.session.commit()
        temp1 = Team.query.filter_by(name=form.teamname.data).first()
        temp2 = User.query.filter_by(id=id).first()
        temp2.in_team = True
        teamuserrelation = TeamUserRelation()
        teamuserrelation.team_id = temp1.id
        teamuserrelation.user_id = id
        teamuserrelation.is_master = True
        teamuserrelation.is_accepted = True
        db.session.add(teamuserrelation)
        db.session.add(temp2)
        db.session.commit()
        return redirect(url_for('student.team'))
    return render_template('student/team/create.html', form=form,id=id)
@blueprint.route('/team/myTeam')
def my_team():
    return render_template('student/team/myTeam.html')





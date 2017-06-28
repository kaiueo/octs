from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course,Term,Team,TeamUserRelation,User
from octs.user.models import Course,Term,Team,TeamUserRelation,User
from .forms import TeamForm
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


@blueprint.route('/team/myTeam/<id>')
def my_team(id):
    temp = TeamUserRelation.query.filter_by(user_id=id).first()
    teamid = temp.team_id
    turs = TeamUserRelation.query.filter(TeamUserRelation.is_accepted == False).filter(TeamUserRelation.team_id == teamid).all()
    userlist = [tur.user for tur in turs]
    if temp.is_master:
        return render_template('student/team/mngmyTeam.html',list=userlist)
    form=TeamRequireForm()
    teamlist=Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(
    TeamUserRelation.team_id==Team.id).filter(TeamUserRelation.is_master==True).join(
    User,TeamUserRelation.user_id==User.id).filter(TeamUserRelation.user_id==User.id).add_columns(
    Team.name,User.username,Team.status,Team.id,User.user_id,User.in_team)

    return render_template('student/team.html',list=teamlist,form=form)
@blueprint.route('/team/create')
def create_team():
    return render_template('student/team/create.html')

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

@blueprint.route('/team/<id>')
def my_team(id):
    t1 = TeamUserRelation.query.filter_by(user_id=id).first()
    flag = 1

    if t1 :
        teamid = t1.team_id
        tars = TeamUserRelation.query.filter(TeamUserRelation.team_id == teamid).filter(TeamUserRelation.is_accepted == True).all()
        turs = TeamUserRelation.query.filter(TeamUserRelation.is_accepted == False).filter(
            TeamUserRelation.team_id == teamid).all()
        userlist = [tur.user for tur in turs]
        userList = [tar.user for tar in tars]
        myteam = Team.query.filter_by(id=teamid).first()
        if t1.is_master:
            return render_template('student/team/mngmyTeam.html',myteam=myteam,list=userlist,userList=userList)
        else:
            return render_template('student/team/myTeam.html',myteam=myteam,flag=flag,userList=userList)
    else:
        flag = 0
        return render_template('student/team/myTeam.html',flag=flag)

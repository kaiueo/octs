from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Course,Term,Team,TeamUserRelation,User
from octs.user.models import Course,Term,Team,TeamUserRelation,User, Message
from .forms import TeamForm
from .forms import CourseForm
from octs.database import db
from flask_login import current_user
import time
import datetime
from octs.student.forms import TeamRequireForm


blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('student/index.html')

@blueprint.route('/course/')
def course():
    courseList = current_user.courses
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
    flash('已提交申请')
    return redirect(url_for('student.team'))

@blueprint.route('/team/<id>')
def my_team(id):
    t1 = TeamUserRelation.query.filter_by(user_id=id).first()
    flag = 1

    if t1 :
        teamid = t1.team_id
        tars = TeamUserRelation.query.filter(TeamUserRelation.team_id == teamid).filter(TeamUserRelation.is_accepted == True).all()
        turs = TeamUserRelation.query.filter(TeamUserRelation.is_accepted == False).filter(
            TeamUserRelation.team_id == teamid).all()
        userlist = [tur.user for tur in turs if tur.user.in_team==True] # l小写
        apply_num = len(userlist)
        userList = [tar.user for tar in tars]
        myteam = Team.query.join(TeamUserRelation,Team.id==TeamUserRelation.team_id).filter(Team.id==teamid).add_columns(
        Team.id,Team.name,Team.status,TeamUserRelation.user_id,TeamUserRelation.is_accepted).first()
        if t1.is_master:
            return render_template('student/team/mngmyTeam.html',userid=id,myteam=myteam,applylist=userlist,userList=userList, num=apply_num)
        else:
            return render_template('student/team/myTeam.html',myteam=myteam,flag=flag,userList=userList, num=apply_num)
    else:
        flag = 0
        return render_template('student/team/myTeam.html',flag=flag)

@blueprint.route('team/<userid>/apply/<id>')
def team_apply(userid, id):
    team = Team.query.filter_by(id=id).first()
    turs = TeamUserRelation.query.join(User, User.id == TeamUserRelation.user_id).filter(
        TeamUserRelation.is_accepted == False).filter(TeamUserRelation.team_id == team.id).add_columns(User.id,
                                                                                                      User.user_id,
                                                                                                      User.username,
                                                                                                      User.gender)
    turs = [tur for tur in turs if tur.is_accepted==False]
    for tur in turs:
        user_id = tur.user_id
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(tur)
        user.in_team = False
        Message.sendMessage(11, user.id, '你的团队加入申请已被拒绝')
        db.session.add(user)
    team.status = 1
    db.session.add(team)
    db.session.commit()
    flash('成功')
    return redirect(url_for('student.my_team', id=userid))

@blueprint.route('/team/permit/<id>/<userid>')
def permit(id,userid):
    stuPermit=TeamUserRelation.query.filter_by(user_id=userid).first()
    stuPermit.is_accepted=True
    db.session.add(stuPermit)
    db.session.commit()
    Message.sendMessage(id, userid, '你的团队加入申请已被接受！')
    flash('已同意该同学申请！')
    return redirect(url_for('student.my_team',id=id))

@blueprint.route('team/reject/<id>/<userid>')
def reject(id,userid):
    temp = TeamUserRelation.query.filter_by(user_id=userid).first()
    db.session.delete(temp)
    stu=User.query.filter_by(id=userid).first()
    stu.in_team=False
    db.session.add(stu)
    db.session.commit()
    flash('                                              已拒绝该同学')
    Message.sendMessage(id,userid,'你的团队加入申请被拒绝！另请高明吧！')
    return redirect(url_for('student.my_team',id=id))



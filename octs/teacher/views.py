from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course,Task,Term,Team,TeamUserRelation,User, Message
from .forms import CourseForm,TaskForm
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

@blueprint.route('/task')
def task():
    taskList = Task.query.all()
    return render_template('teacher/task.html',list = taskList)

@blueprint.route('/task/add',methods = ['GET','POST'])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task()
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.teacher = form.teacher.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('teacher.task'))
    return render_template('teacher/add.html',form=form)

@blueprint.route('/task/edit/<id>',methods = ['GET','POST'])
def task_edit(id):
    form = TaskForm()

    task = Task.query.filter_by(id = id).first()
    if form.validate_on_submit():
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.teacher = form.teacher.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('teacher.task'))

    form.taskname.data = task.name
    form.starttime.data = task.start_time
    form.endtime.data = task.end_time
    form.teacher.data =task.teacher
    return render_template('teacher/edit.html',form = form)

@blueprint.route('/task/delete/<id>')
def delete(id):
    task = Task.query.filter_by(id = id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('teacher.task'))

@blueprint.route('/team',methods=['GET', 'POST'])
def team():
    teamlist = Team.query.join(TeamUserRelation, TeamUserRelation.team_id == Team.id).filter(
        TeamUserRelation.team_id == Team.id).filter(TeamUserRelation.is_master == True).join(
        User, TeamUserRelation.user_id == User.id).filter(TeamUserRelation.user_id == User.id).add_columns(
        Team.name, User.username, Team.status, Team.id, User.user_id, User.in_team)
    return render_template('teacher/team.html',list=teamlist)

@blueprint.route('/team/permit/<teacherid>/<teamid>')
def permit(teacherid,teamid):
    team=Team.query.filter(Team.id==teamid).first()
    team.status=3
    db.session.add(team)
    db.session.commit()
    stulist=TeamUserRelation.query.filter(TeamUserRelation.team_id==teamid).filter(TeamUserRelation.is_accepted==True).all()
    for stu in stulist:
        Message.sendMessage(teacherid,stu.user_id,'提交团队申请已通过')
    flash('已通过该团队申请！')
    return redirect(url_for('teacher.team'))
@blueprint.route('/team/reject/<teacherid>/<teamid>')
def reject(teacherid,teamid):
    team=Team.query.filter(Team.id==teamid).first()
    team.status=2
    db.session.add(team)
    teamuser=TeamUserRelation.query.filter(TeamUserRelation.team_id==teamid).all()
    for stu in teamuser:
        user=User.query.filter(User.id==stu.user_id).first()
        user.in_team=False
        Message.sendMessage(teacherid,user.id,'提交申请已被驳回')
        db.session.add(user)
        db.session.delete(stu)
    db.session.commit()
    flash('已驳回该团队申请！')
    return redirect(url_for('teacher.team'))









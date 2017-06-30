from flask import Blueprint, flash, redirect, render_template, request, url_for,send_from_directory, abort
from octs.user.models import Course,Task, User, Message, Team,TeamUserRelation, File
from .forms import CourseForm,TaskForm, FileForm
from octs.database import db
from flask_login import current_user
from octs.extensions import data_uploader
import time
import os
from pypinyin import lazy_pinyin

blueprint = Blueprint('teacher', __name__, url_prefix='/teacher',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('teacher/index.html')


@blueprint.route('/<teacherid>/course/')
def course(teacherid):
    teacher = User.query.filter_by(id=teacherid).first()
    courseList = teacher.courses
    return render_template('teacher/course.html', list=courseList)


@blueprint.route('/<teacherid>/course/edit/<id>',methods=['GET','POST'])
def course_edit(teacherid, id):
    course = Course.query.filter_by(id=id).first()
    form = CourseForm()
    if form.validate_on_submit():
        course.course_introduction = form.course_introduction.data
        course.course_outline=form.course_outline.data
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher.course', teacherid=teacherid))

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

@blueprint.route('/<courseid>/task')
def task(courseid):
    taskList = Task.query.filter_by(course_id=courseid).all()
    return render_template('teacher/task.html',list = taskList, courseid=courseid)

@blueprint.route('/<courseid>/task/add',methods = ['GET','POST'])
def add(courseid):
    form = TaskForm()
    if form.validate_on_submit():
        task = Task()
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.teacher = current_user.name
        task.course_id = form.content.data
        course = Course.query.filter_by(id=courseid).first()
        course.tasks.append(task)
        db.session.add(task)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('teacher.task', courseid=courseid))
    return render_template('teacher/add.html',form=form, courseid=courseid)

@blueprint.route('/<courseid>/task/edit/<id>',methods = ['GET','POST'])
def task_edit(courseid, id):
    form = TaskForm()
    task = Task.query.filter_by(id = id).first()
    if form.validate_on_submit():
        task.name = form.taskname.data
        task.start_time = form.starttime.data
        task.end_time = form.endtime.data
        task.content = form.content.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('teacher.task', courseid=courseid))

    form.taskname.data = task.name
    form.starttime.data = task.start_time
    form.endtime.data = task.end_time
    form.content.data = task.content
    return render_template('teacher/edit.html',form = form, courseid=courseid, taskid=id)

@blueprint.route('/<courseid>/task/delete/<id>')
def delete(courseid, id):
    task = Task.query.filter_by(id = id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('teacher.task', courseid=courseid))

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
@blueprint.route('team/detail/<teamid>')
def team_detail(teamid):
    teamlist=Team.query.filter(Team.id==teamid).join(TeamUserRelation,TeamUserRelation.team_id==Team.id).join(
        User,User.id==TeamUserRelation.user_id).add_columns(User.name,User.gender,User.user_id).all()
    return render_template('teacher/teamdetail.html',list=teamlist)
@blueprint.route('team/adjust/<teacherid>')
def to_adjust(teacherid):
    teamlist1=Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(Team.status==1).filter(
        TeamUserRelation.is_master==True).join(User,User.id==TeamUserRelation.user_id).add_columns(
        Team.name,Team.status,User.username).all()
    teamlist2 = Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(Team.status==3).filter(
        TeamUserRelation.is_master==True).join(User,User.id==TeamUserRelation.user_id).add_columns(
        Team.name,Team.status,User.username).all()
    teamlist=teamlist1+teamlist2
    return render_template('teacher/adjust.html',teacher_id=teacherid,list=teamlist)

@blueprint.route('/<courseid>/task/<taskid>/files', methods=['GET', 'POST'])
def task_files(courseid, taskid):
    form = FileForm()
    file_records = File.query.filter_by(task_id=taskid).all()
    if form.validate_on_submit():
        for file in request.files.getlist('file'):
            file_record = File()
            file_record.user_id = current_user.id
            file_record.task_id = taskid

            filename = file.filename
            file_record.name = filename

            filetype = filename.split('.')[-1]
            tmpname = str(current_user.id) + '-' + str(time.time())
            file.filename = tmpname + '.' + filetype

            file_record.directory = data_uploader.path('', folder='course')
            file_record.real_name = file.filename

            file_record.path = data_uploader.path(file.filename, folder='course')

            data_uploader.save(file, folder='course')

            db.session.add(file_record)
        db.session.commit()
        return redirect(url_for('teacher.task_files', courseid=courseid, taskid=taskid))
    return render_template('teacher/file_manage.html',form=form, file_records=file_records, courseid=courseid, taskid=taskid)

@blueprint.route('/<courseid>/task/<taskid>/files/delete/<fileid>', methods=['GET', 'POST'])
def task_file_delete(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    os.remove(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('teacher.task_files', courseid=courseid, taskid=taskid))

@blueprint.route('/<courseid>/task/<taskid>/files/download/<fileid>')
def task_file_download(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True, attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)




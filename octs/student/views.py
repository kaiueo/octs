from flask import Blueprint, flash, redirect, render_template, request, send_from_directory,url_for,abort,send_file
from octs.user.models import Course,Term,Team,TeamUserRelation,User,Task,File,Source,TaskTeamRelation
from octs.user.models import Course,Term,Team,TeamUserRelation,User, Message, Tag, UserScore
from .forms import TeamForm
from .forms import CourseForm,FileForm
from octs.database import db
from flask_login import current_user
from octs.extensions import data_uploader
import time
import datetime
import os, zipfile,xlwt
from octs.student.forms import TeamRequireForm
from pypinyin import lazy_pinyin
from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField,FileField, FieldList
from wtforms.validators import DataRequired, Email, EqualTo, Length


blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/course/')
def course():
    courseList = current_user.courses
    userid = current_user.id
    flag = 0
    team = TeamUserRelation.query.filter_by(user_id=userid).first()
    if(team == None ):
        flag = 1
    else:
        if(team.is_master == False):
            flag = 1
        else:
            flag = 0

    return render_template('student/course/course.html', list=courseList,flag=flag)


@blueprint.route('/checkterm/')
def checkterm():
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    time_now = datetime.date.fromtimestamp(time.time())
    return render_template('student/checkterm.html', list=termList,nowtime=time_now)

@blueprint.route('/mainpage/')
def home():
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
    course = Course.query.order_by(Course.id.desc()).first()
    if form.validate_on_submit():
        team = Team()
        team.name = form.teamname.data
        team.status = 0
        course.teams.append(team)
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
        db.session.add(course)
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

@blueprint.route('/team/<userid>/apply/<id>')
def team_apply(userid, id):
    team = Team.query.filter_by(id=id).first()
    user = User.query.filter(User.id==userid).first()
    flag = True
    number = TeamUserRelation.query.filter(TeamUserRelation.team_id==team.id).filter(TeamUserRelation.is_accepted==True).count()
    if int(number) < int(user.team_min):
        flag=False
        flash('团队人数不足！')
    if flag:
        turs = TeamUserRelation.query.join(User, User.id == TeamUserRelation.user_id).filter(
        TeamUserRelation.is_accepted == False).filter(TeamUserRelation.team_id == team.id).add_columns(User.id,
                                                                                                      User.user_id,
                                                                                                      User.username,
                                                                                                      User.gender).all()
        turs = [tur for tur in turs if tur[0].is_accepted==False]
        for tur in turs:
            user = User.query.filter_by(id=tur[1]).first()
            db.session.delete(tur[0])
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
    flash('已同意该同学的申请！')
    return redirect(url_for('student.my_team',id=id))

@blueprint.route('/team/reject/<id>/<userid>')
def reject(id,userid):
    temp = TeamUserRelation.query.filter_by(user_id=userid).first()
    db.session.delete(temp)
    stu=User.query.filter_by(id=userid).first()
    stu.in_team=False
    db.session.add(stu)
    db.session.commit()
    flash('已拒绝该同学')
    Message.sendMessage(id,userid,'你的团队加入申请被拒绝！另请高明吧！')
    return redirect(url_for('student.my_team',id=id))


@blueprint.route('/<courseid>/tasklist')
def tasklist(courseid):
    tasklist = Task.query.filter_by(course_id = courseid).all()
    return render_template('student/course/tasklist.html', list=tasklist)


@blueprint.route('/course/tasklist/task/<taskid>')
def task(taskid):
    taskid = taskid
    flag = 0
    tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()

    if(tur == None or tur.is_accepted == False ):
        flag = 0
    else:
        team = Team.query.filter_by(id=tur.team_id).first()
        if(team.status!=3):
            flag = 0
        else:
            flag = 1

    task = Task.query.filter_by(id=taskid).first()
    return render_template('student/course/task.html',task = task,flag=flag)

@blueprint.route('/course/<courseid>/tasklist/task/<taskid>/files', methods=['GET', 'POST'])
def task_files(courseid, taskid):
    form = FileForm()

    # tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    # teamid = tur.team_id
    # mastersearch = TeamUserRelation.query.filter(TeamUserRelation.team_id == teamid).filter(
    #     TeamUserRelation.is_master == True).first()
    # masterid = mastersearch.user_id

    user_ist = Course.query.filter_by(id=courseid).first().users
    teachers = [user for user in user_ist if user.roleString=='teacher']

    file_records = []
    for teacher in teachers:
        file_list = File.query.filter_by(user_id=teacher.id).all()
        file_records.extend(file_list)

    file_records = [file_record for file_record in file_records if file_record.task_id==int(taskid)]


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
        return redirect(url_for('student.task_files', courseid=courseid, taskid=taskid))
    print(file_records)
    return render_template('student/file_manage.html',form=form, file_records=file_records, courseid=courseid, taskid=taskid)

@blueprint.route('/course/<courseid>/tasklist/task/<taskid>/download')
def task_file_download_zip(courseid, taskid):
    tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    teamid = tur.team_id
    foldername = data_uploader.path('', folder='course/'+str(courseid)+'/teacher/tasks/'
                                                                      +str(taskid))
    filename = os.path.join(data_uploader.path('', folder='tmp'), 'taskfiles.zip')
    zip_download = zipfolder(foldername, filename)
    return send_file(filename, as_attachment=True)


@blueprint.route('/<courseid>/checktask/<taskid>/files/download/<fileid>')
def task_file_download(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True, attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)

@blueprint.route('/course/<courseid>/tasklist/task/<taskid>/source',methods=['GET','POST'])
def source(courseid, taskid):
        form = FileForm()
        flag = 0
        tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
        teamid = tur.team_id
        mastersearch = TeamUserRelation.query.filter(TeamUserRelation.team_id==teamid).filter(TeamUserRelation.is_master==True).first()
        masterid = mastersearch.user_id

        ttr = TaskTeamRelation.query.filter(TaskTeamRelation.team_id==teamid).filter(TaskTeamRelation.task_id==taskid).first()
        task = Task.query.filter_by(id=taskid).first()
        submit_time = task.submit_num
        if( ttr!= None ):
            submitted_time = ttr.submit_num
            rest_time = submit_time - submitted_time
        else:
            rest_time = submit_time

        if(tur.is_master==True):
            flag = 1
        else:
            flag = 0

        time_flag = 0
        task_record = Task.query.filter_by(id=taskid).first()
        task_endtime = task_record.end_time
        time_now = datetime.datetime.fromtimestamp(time.time())
        if (time_now > task_endtime):
            time_flag = 1
        else:
            time_flag = 0

        sub_flag = 0
        if (submit_time-ttr.submit_num>0):
            sub_flag = 1
        else:
            sub_flag = 0

        file_records = File.query.filter(File.task_id==taskid).filter(File.user_id==masterid ).all()
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

                file_record.directory = data_uploader.path('', folder='course/'+str(courseid)+'/student/tasks/'
                                                                      +str(taskid)+'/'+str(teamid))
                file_record.real_name = file.filename

                file_record.path = data_uploader.path(file.filename, folder='course/'+str(courseid)+'/student/tasks/'
                                                                      +str(taskid)+'/'+str(teamid))

                data_uploader.save(file, folder='course/'+str(courseid)+'/student/tasks/'
                                                                      +str(taskid)+'/'+str(teamid))

                db.session.add(file_record)
                db.session.commit()

                taskteamrelation = TaskTeamRelation.query.filter(TaskTeamRelation.task_id==taskid).filter(TaskTeamRelation.team_id==teamid).first()
                # taskteamrelation.team_id = teamid
                # taskteamrelation.task_id = taskid
                taskteamrelation.submit_num = ttr.submit_num + 1
                db.session.add(taskteamrelation)
                db.session.commit()

            return redirect(url_for('student.source', courseid=courseid, taskid=taskid))
        return render_template('student/course/task_file_manage.html', form=form, file_records=file_records, courseid=courseid,
                                   taskid=taskid,flag=flag,resttime=rest_time,timeflag=time_flag,sub_flag=sub_flag)




@blueprint.route('/<courseid>/task/<taskid>/source/delete/<fileid>', methods=['GET', 'POST'])
def source_delete(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    os.remove(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('student.source', courseid=courseid, taskid=taskid))

@blueprint.route('/<courseid>/checktask/<taskid>/source/download/<fileid>')
def source_download(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True, attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)

def zipfolder(foldername,filename):
    '''
        zip folder foldername and all its subfiles and folders into
        a zipfile named filename
    '''
    zip_download=zipfile.ZipFile(filename,'w',zipfile.ZIP_DEFLATED)
    for root,dirs,files in os.walk(foldername):
        print(root, dirs, files)
        for filename in files:
            zip_download.write(os.path.join(root,filename), arcname=os.path.join(os.path.basename(root) ,filename))
    zip_download.close()
    return zip_download

@blueprint.route('/<courseid>/task/<taskid>/files/download')
def task_file_download_zip_source(courseid, taskid):
    tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    teamid = tur.team_id
    foldername = data_uploader.path('', folder='course/'+str(courseid)+'/student/tasks/'
                                                                      +str(taskid)+'/'+str(teamid))
    filename = os.path.join(data_uploader.path('', folder='tmp'), 'taskfiles.zip')
    zip_download = zipfolder(foldername, filename)
    return send_file(filename, as_attachment=True)

@blueprint.route('/course/give_grade', methods=['GET', 'POST'])
def give_grade():
    team = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    turs = TeamUserRelation.query.filter_by(team_id=team.team_id).all()
    user_ids = [tur.user_id for tur in turs]
    for tur in turs:
        user = UserScore.query.filter_by(user_id=tur.user_id).first()
        if(user == None):
            new_user = UserScore()
            new_user.user_id = tur.user_id
            db.session.add(new_user)
            db.session.commit()
    user_grades = []
    user_names = []
    for user_id in user_ids:
        user = User.query.filter_by(id=user_id).first()
        user_names.append(user.name)
        us = UserScore.query.filter_by(user_id=user_id).first()
        user_grades.append(us)

    user_num = len(turs)
    class GradeForm(Form):
        pass

    for i in range(user_num):
        setattr(GradeForm, 'grade'+str(i), FloatField(user_names[i], validators=[DataRequired()]))

    form = GradeForm()
    if form.validate_on_submit():
        for i in range(user_num):
            user_grades[i].grade = getattr(form, 'grade'+str(i)).data
            db.session.add(user_grades[i])
        db.session.commit()

    for i in range(user_num):
        getattr(form, 'grade'+str(i)).data = user_grades[i].grade

    return render_template("student/course/give_grade.html",form=form, user_num=user_num)

@blueprint.route('/source/<courseid>')
def course_source(courseid):
    course = Course.query.filter_by(id=courseid).first()
    tags = course.tags
    tag_names = {}
    file_records = File.query.filter_by(course_id=courseid).all()
    for file_record in file_records:
        tag = Tag.query.filter_by(id=file_record.tag_id).first()
        tag_names[file_record.tag_id] = tag.name
    return render_template('student/source.html', file_records=file_records, courseid=courseid, tags=tags, tag_names=tag_names)

@blueprint.route('/source/<courseid>/tag/<tagid>')
def course_source_tag(courseid, tagid):
    course = Course.query.filter_by(id=courseid).first()
    tags = course.tags
    file_records = File.query.filter_by(tag_id=tagid).all()
    return render_template('student/source_tag.html', file_records=file_records, courseid=courseid, tags=tags, tagid=tagid)

@blueprint.route('/source/<courseid>/files/download')
def source_file_download_zip(courseid):
    foldername = data_uploader.path('',folder='course/'+str(courseid)+'/teacher/source')
    filename = os.path.join(data_uploader.path('',folder='tmp'),'sourcefiles.zip')
    zip_download = zipfolder(foldername,filename)
    return send_file(filename,as_attachment=True)

@blueprint.route('<courseid>/source/files/download/<fileid>')
def course_source_download(courseid,fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True,
                                   attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)

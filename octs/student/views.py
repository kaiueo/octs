from flask import Blueprint, flash, redirect, render_template, request, send_from_directory,url_for,abort,send_file
from octs.user.models import Course,Term,Team,TeamUserRelation,User,Task,File,Source
from octs.user.models import Course,Term,Team,TeamUserRelation,User, Message
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


blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/course/')
def course():
    courseList = current_user.courses
    return render_template('student/course/course.html', list=courseList)


@blueprint.route('/checkterm/')
def checkterm():
    termList = Term.query.order_by(Term.start_time).all()
    termList = list(reversed(termList))
    time_now = datetime.date.fromtimestamp(time.time())
    return render_template('student/checkterm.html', list=termList,endtime=termList[0],nowtime=time_now)

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

@blueprint.route('/team/reject/<id>/<userid>')
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


@blueprint.route('/<courseid>/tasklist')
def tasklist(courseid):
    tasklist = Task.query.filter_by(course_id = courseid).all()
    return render_template('student/course/tasklist.html', list=tasklist)


@blueprint.route('/course/tasklist/task/<taskid>')
def task(taskid):
    taskid = taskid
    flag = 0
    tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    if(tur == None or tur.is_accepted == False):
        flag = 0
    else:
        flag = 1
    task = Task.query.filter_by(id=taskid).first()
    return render_template('student/course/task.html',task = task,flag=flag)

@blueprint.route('/course/<courseid>/tasklist/task/<taskid>/files', methods=['GET', 'POST'])
def task_files(courseid, taskid):
    form = FileForm()
    tur = TeamUserRelation.query.filter_by(user_id=current_user.id).first()
    user_ist = Course.query.filter_by(id=courseid).first().users
    teachers = [user for user in user_ist if user.roleString=='teacher']

    teamid = tur.team_id
    mastersearch = TeamUserRelation.query.filter(TeamUserRelation.team_id == teamid).filter(
        TeamUserRelation.is_master == True).first()

    masterid = mastersearch.user_id
    file_records = []
    for teacher in teachers:
        file_list = File.query.filter_by(user_id=teacher.id).all()
        print('fl', file_list)
        file_records.extend(file_list)
    print('fl1', file_records)
    print('tid', taskid)
    file_records = [file_record for file_record in file_records if file_record.task_id==int(taskid)]
    print('fl2', file_records)

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
    return render_template('student/file_manage.html',form=form, file_records=file_records, courseid=courseid, taskid=taskid,masterid=masterid)

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
        if(tur.is_master==True):
            flag=1
        else:
            flag=0
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
            return redirect(url_for('student.source', courseid=courseid, taskid=taskid))
        return render_template('student/course/task_file_manage.html', form=form, file_records=file_records, courseid=courseid,
                                   taskid=taskid,flag=flag)




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



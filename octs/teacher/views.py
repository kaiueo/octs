from flask import Blueprint, flash, redirect, render_template, request, url_for,send_from_directory, abort, make_response, send_file, session
from octs.user.models import Course,Task, User, Message, Team,TeamUserRelation, File,Source,Term,TaskTeamRelation
from .forms import CourseForm,TaskForm, FileForm,TaskScoreForm
from octs.database import db
from flask_login import current_user
from octs.extensions import data_uploader
import time
import os,zipfile
from pypinyin import lazy_pinyin
import xlwt

blueprint = Blueprint('teacher', __name__, url_prefix='/teacher',static_folder='../static')

@blueprint.route('/<teacherid>/course/')
def course(teacherid):
    teacher = User.query.filter_by(id=teacherid).first()
    courseList = teacher.courses
    term = Term.query.order_by(Term.id.desc()).first()
    return render_template('teacher/course.html', list=courseList,termid=term.id)

@blueprint.route('/<courseid>/task/<taskid>')
def task_detail(courseid,taskid):
    taskList = Task.query.filter_by(id=taskid).all()
    return render_template('teacher/taskdetail.html',list=taskList,courseid=courseid)


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
def home():
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
        task.submit_num = form.subnum.data
        task.weight = form.weight.data
        task.teacher = current_user.name
        task.content = form.content.data
        course = Course.query.filter_by(id=courseid).first()
        course.tasks.append(task)
        teams = course.teams
        for team in teams:
            ttr = TaskTeamRelation()
            ttr.team = team
            ttr.task = task
            db.session.add(ttr)
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
        task.submit_num = form.subnum.data
        task.weight = form.weight.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('teacher.task', courseid=courseid))

    form.taskname.data = task.name
    form.starttime.data = task.start_time
    form.endtime.data = task.end_time
    form.content.data = task.content
    form.subnum.data = task.submit_num
    form.weight.data = task.weight
    return render_template('teacher/edit.html',form = form, courseid=courseid, taskid=id)

@blueprint.route('/<courseid>/task/delete/<taskid>',methods=['GET','POST'])
def delete(courseid, taskid):
    file_records= File.query.filter_by(task_id=taskid).all()
    for file_record in file_records:
        os.remove(file_record.path)
        db.session.delete(file_record)

    task = Task.query.filter_by(id=taskid).first()
    ttrs = TaskTeamRelation.query.filter_by(task_id=task.id).all()
    for ttr in ttrs:
        db.session.delete(ttr)
    db.session.delete(task)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('teacher.task', courseid=courseid))

@blueprint.route('/team',methods=['GET', 'POST'])
def team():
    teamlist = Team.query.join(TeamUserRelation, TeamUserRelation.team_id == Team.id).filter(
        TeamUserRelation.team_id == Team.id).filter(TeamUserRelation.is_master == True).join(
        User, TeamUserRelation.user_id == User.id).filter(TeamUserRelation.user_id == User.id).add_columns(
        Team.name, User.username, Team.status, Team.id, User.user_id, User.in_team)
    return render_template('teacher/team.html',list=teamlist)

@blueprint.route('/task/score<taskid>/download')
def score_download(taskid):
    teamidList = TaskTeamRelation.query.filter_by(task_id=taskid).all()
    teams = []
    for teamid in teamidList:
        team = Team.query.filter_by(id=teamid.team_id).first()
        teams.append(team)
    task = Task.query.filter_by(id=taskid).first()

    book = xlwt.Workbook()

    alignment = xlwt.Alignment()  # Create Alignment
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle()  # Create Style
    style.alignment = alignment  # Add Alignment to Style

    sheet1 = book.add_sheet('本次作业信息('+task.name+')',cell_overwrite_ok=True)
    row0 = ['团队id','团队名称','作业得分']
    for i in range(0,len(row0)):
        sheet1.write(0,i,row0[i], style)
    row_num =1
    for team in teams:
        sheet1.write(row_num,0,team.id,style)
        sheet1.write(row_num,1,team.name,style)
        sheet1.write(row_num,2,team.score,style)
    filename = 'score_table_'+ str(time.time()) + '.xls'
    book.save(os.path.join(data_uploader.path('',folder='tmp'),filename))
    return send_from_directory(data_uploader.path('', folder='tmp'), filename, as_attachment=True)

@blueprint.route('/team/download')
def team_download():
    teams = Team.query.filter_by(status=3).all()
    book = xlwt.Workbook()

    alignment = xlwt.Alignment()  # Create Alignment
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle()  # Create Style
    style.alignment = alignment  # Add Alignment to Style

    sheet1 = book.add_sheet('团队信息', cell_overwrite_ok=True)
    row0 = ['团队id', '团队名称', '姓名', '学号', '性别', 'Master']
    for i in range(0, len(row0)):
        sheet1.write(0, i, row0[i])

    row_num = 1
    for team in teams:
        turs = TeamUserRelation.query.filter_by(team_id=team.id).all()
        turs_length = len(turs)
        sheet1.write_merge(row_num, row_num + turs_length - 1, 0, 0, team.id, style)
        sheet1.write_merge(row_num, row_num + turs_length - 1, 1, 1, team.name, style)
        for i in range(turs_length):
            if turs[i].is_accepted:
                sheet1.write(row_num+i, 2, turs[i].user.name)
                sheet1.write(row_num + i, 3, turs[i].user.user_id)
                gender = '男' if turs[i].user.gender==False else '女'
                sheet1.write(row_num + i, 4, gender)
                if turs[i].is_master == True:
                    sheet1.write(row_num + i, 5, '√')
        row_num = row_num + turs_length
    filename = 'team_table_' + str(time.time()) + '.xls'
    book.save(os.path.join(data_uploader.path('', folder='tmp'), filename))
    return send_from_directory(data_uploader.path('', folder='tmp'), filename, as_attachment=True)


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

@blueprint.route('/team/adjustion/<teacherid>')
def to_adjust(teacherid):
    teamlist1=Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(Team.status==1).filter(
        TeamUserRelation.is_master==True).join(User,User.id==TeamUserRelation.user_id).add_columns(
        Team.name,Team.status,User.username,Team.id).all()
    teamlist2 = Team.query.join(TeamUserRelation,TeamUserRelation.team_id==Team.id).filter(Team.status==3).filter(
        TeamUserRelation.is_master==True).join(User,User.id==TeamUserRelation.user_id).add_columns(
        Team.name,Team.status,User.username).all()
    teamlist=teamlist1+teamlist2
    return render_template('teacher/adjust.html',teacher_id=teacherid,list=teamlist)

@blueprint.route('/team/adjustion/<teacherid>/adjust/<teamid>',methods=['GET', 'POST'])
def team_adjust(teacherid,teamid):
    teamlist = Team.query.filter(Team.id == teamid).join(TeamUserRelation, TeamUserRelation.team_id == Team.id).join(
        User, User.id == TeamUserRelation.user_id).add_columns(User.name, User.gender, User.user_id,TeamUserRelation.user_id,Team.id).all()
    otherteam=Team.query.filter(Team.id!=teamid).filter(Team.status==1).all()
    if session.get('deleted_stu') is None:
        session['deleted_stu'] = []
    translist = session['deleted_stu']
    return render_template('teacher/team_adjust.html',list=teamlist,other_team=otherteam,translist=translist)

@blueprint.route('/team/adjustion/<teacherid>/adjust/<teamid>/<userid>',methods=['GET', 'POST'])
def adjust_trans(teacherid,userid,teamid):
    teamlist = Team.query.filter(Team.id == teamid).join(TeamUserRelation, TeamUserRelation.team_id == Team.id).join(
        User, User.id == TeamUserRelation.user_id).add_columns(User.name, User.gender, User.user_id,
                                                               TeamUserRelation.user_id, Team.id).all()
    user=User.query.join(TeamUserRelation,TeamUserRelation.user_id==userid).filter(User.id==userid).add_columns(
        User.id,User.name,User.gender,TeamUserRelation.is_master).first()
    user_dict = {'id':user.id,'name':user.name,'gender':user.gender}
    if session.get('deleted_stu') is None:
        session['deleted_stu'] = []
    translist = session['deleted_stu']
    flag=True
    for ad_stu in translist:
        if(ad_stu['id']==user.id):
            flag=False
            flash('该学生已在调整名单中！')
    if user.is_master==True:
        flag=False
        flash('该学生是本队组长！不能调整！')
    if flag:
        userlist=TeamUserRelation.query.filter(TeamUserRelation.user_id==user.id).first()
        userlist.is_adjust=True
        db.session.add(userlist)
        db.session.commit()
        translist.append(user_dict)
    session['deleted_stu'] = translist

    return redirect(url_for('teacher.team_adjust', teacherid=teacherid, teamid=teamid))

@blueprint.route('/team/adjustion/<teacherid>/adjust/<teamid>/add/<userid>',methods=['GET', 'POST'])
def adjust_add(teacherid,userid,teamid):
    userlist=TeamUserRelation.query.filter(TeamUserRelation.user_id==userid).first()
    if(int(teamid)==int(userlist.team_id)):
        flash('该生已在本团队了！')
    else:
        userlist.team_id=teamid
        userlist.is_adjust=False
        db.session.add(userlist)
        db.session.commit()
        Message.sendMessage(teacherid,userid,'你已经被老师调整至其他组！请注意查看')
        flash('已将该学生调整到该团队！')
        translist=session['deleted_stu']
        for user in translist:
            if user['id'] == int(userid):
                translist.remove(user)
        session['deleted_stu']=translist
    return redirect(url_for('teacher.team_adjust', teacherid=teacherid, teamid=teamid))

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

            file_record.directory = data_uploader.path('', folder='course/'+str(courseid)+'/teacher/tasks/'+str(taskid))
            file_record.real_name = file.filename

            file_record.path = data_uploader.path(file.filename, folder='course/'+str(courseid)+'/teacher/tasks/'+str(taskid))

            data_uploader.save(file, folder='course/'+str(courseid)+'/teacher/tasks/'+str(taskid))

            db.session.add(file_record)
        db.session.commit()
        return redirect(url_for('teacher.task_files', courseid=courseid, taskid=taskid))
    return render_template('teacher/file_manage.html',form=form, file_records=file_records, courseid=courseid, taskid=taskid)

@blueprint.route('/<courseid>/task/<taskid>/files/delete/<fileid>/<userid>', methods=['GET', 'POST'])
def task_file_delete(courseid, taskid, fileid,userid):
    file_record = File.query.filter_by(id=fileid).first()
    os.remove(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('teacher.task_files', courseid=courseid, taskid=taskid,userid = userid))

@blueprint.route('/<courseid>/task/<taskid>/files/delete/<fileid>', methods=['GET', 'POST'])
def student_task_file_delete(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    os.remove(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('teacher.student_task', courseid=courseid, taskid=taskid))

@blueprint.route('/<courseid>/task/<taskid>/files/download/<fileid>')
def task_file_download(courseid, taskid, fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True, attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)

@blueprint.route('/<courseid>/task/<taskid>/scores')
def task_give_score(courseid,taskid):
    tasklist=Task.query.filter(Task.id==taskid).first()
    if time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))<str(tasklist.end_time):
        flash('这项作业还未截止！暂时不能批改')
        return render_template('teacher/task_score.html',flag=False)
    else:
        task_team_list=TaskTeamRelation.query.join(Task,Task.id==TaskTeamRelation.task_id).join(Team,Team.id==TaskTeamRelation.team_id
            ).filter(TaskTeamRelation.task_id==taskid).add_columns(Team.name,TaskTeamRelation.task_id,TaskTeamRelation.team_id,TaskTeamRelation.score,Task.weight).all()
        task_name=Task.query.filter(Task.id==taskid).first()
        return render_template('teacher/task_score.html', flag=True,list=task_team_list,name=task_name,courseid=courseid)

@blueprint.route('/<courseid>/task/<taskid>/givescore/<teamid>',methods=['GET', 'POST'])
def task_edit_score(courseid,taskid,teamid):
    taskscore=TaskTeamRelation.query.filter(TaskTeamRelation.task_id==taskid).filter(TaskTeamRelation.team_id==teamid).first()
    form = TaskScoreForm()
    if form.validate_on_submit():
        taskscore.score=form.task_score.data
        db.session.add(taskscore)
        db.session.commit()
        flash('已经提交分数！')
        return redirect(url_for('teacher.task_give_score',courseid=courseid,taskid=taskid))

    form.task_score.data=taskscore.score
    return render_template('teacher/set_score.html',form=form,courseid=courseid,taskid=taskid,teamid=teamid)

@blueprint.route('/<courseid>/task<taskid>/scores')
def task_score(courseid,taskid):
    teamidList = TaskTeamRelation.query.filter_by(task_id=taskid).all()
    teams = []
    for teamid in teamidList:
        team = Team.query.filter_by(id=teamid.team_id).first()
        teams.append(team)
    task = Task.query.filter_by(id=taskid).first()
    return render_template('teacher/task_one_score.html',teams=teams,task=task,courseid=courseid,taskid=taskid)

@blueprint.route('/<courseid>/task/<taskid>/files',methods = ['GET','POST'])
def student_task(courseid,taskid):
    form = FileForm()
    course = Course.query.filter_by(id = courseid).first()
    users = course.users
    masters = []
    for user in users:
        tur = TeamUserRelation.query.filter(TeamUserRelation.user_id == user.id).filter(TeamUserRelation.is_master == True).first()
        if tur is not None:
            masters.append(tur)
    print(masters)
    file_records = []
    for master in masters:
        file_records.append((master.team_id ,File.query.filter(File.user_id == master.user_id).filter(File.task_id == int(taskid)).all()))
    print(file_records)
    return render_template('teacher/task_student.html',form = form,file_records=file_records,courseid = courseid,taskid = taskid)

@blueprint.route('/source/<courseid>',methods=['GET','POST'])
def source(courseid):
    ##sourcelist=Source.query.filter_by(course_id=courseid).all()
    ##return render_template('teacher/source.html', list=sourcelist, courseid=courseid)
    form = FileForm()
    file_records = File.query.filter_by(course_id=courseid).all()
    if form.validate_on_submit():
        for file in request.files.getlist('file'):
            file_record = File()
            file_record.user_id = current_user.id
            file_record.course_id = courseid

            filename = file.filename
            file_record.name = filename

            filetype = filename.split('.')[-1]
            tmpname = str(current_user.id) + '-' + str(time.time())
            file.filename = tmpname + '.' + filetype

            file_record.directory = data_uploader.path('', folder='course/'+str(courseid)+'/teacher/source')
            file_record.real_name = file.filename

            file_record.path = data_uploader.path(file.filename, folder='course/'+str(courseid)+'/teacher/source')

            data_uploader.save(file, folder='course/'+str(courseid)+'/teacher/source')

            db.session.add(file_record)
        db.session.commit()
        return redirect(url_for('teacher.source', courseid=courseid))
    return render_template('teacher/source.html', form=form, file_records=file_records, courseid=courseid)

@blueprint.route('<courseid>/source/files/download/<fileid>')
def source_download(courseid,fileid):
    file_record = File.query.filter_by(id=fileid).first()
    if os.path.isfile(file_record.path):
        return send_from_directory(file_record.directory, file_record.real_name, as_attachment=True,
                                   attachment_filename='_'.join(lazy_pinyin(file_record.name)))
    abort(404)

@blueprint.route('<courseid>/source/files/delete/<fileid>')
def source_delete(courseid,fileid):
    file_record = File.query.filter_by(id=fileid).first()
    os.remove(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('teacher.source', courseid=courseid))

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
def task_file_download_zip(courseid, taskid):
    foldername = data_uploader.path('', folder='course/'+str(courseid)+'/teacher/tasks/'+str(taskid))
    filename = os.path.join(data_uploader.path('', folder='tmp'), 'taskfiles.zip')
    zip_download = zipfolder(foldername, filename)
    return send_file(filename, as_attachment=True)

@blueprint.route('/<courseid>/task/<taskid>/studenttask/files/download')
def student_task_file_download_zip(courseid, taskid):
    foldername = data_uploader.path('', folder='course/'+str(courseid)+'/student/tasks/'+str(taskid))
    filename = os.path.join(data_uploader.path('', folder='tmp'), 'taskfiles.zip')
    zip_download = zipfolder(foldername, filename)
    return send_file(filename, as_attachment=True)

@blueprint.route('/source/<courseid>/files/download')
def source_file_download_zip(courseid):
    foldername = data_uploader.path('',folder='course/'+str(courseid)+'/teacher/source')
    filename = os.path.join(data_uploader.path('',folder='tmp'),'sourcefiles.zip')
    zip_download = zipfolder(foldername,filename)
    return send_file(filename,as_attachment=True)

@blueprint.route('/<courseid>/files/download')
def former_task_file_download_zip(courseid):
    foldername = data_uploader.path('', folder='course/'+str(courseid)+'/student')
    filename = os.path.join(data_uploader.path('', folder='tmp'), 'taskfiles.zip')
    zip_download = zipfolder(foldername, filename)
    return send_file(filename, as_attachment=True)

@blueprint.route('/<courseid>/task/submit')
def multi_check(courseid):
    tasks = Task.query.filter_by(course_id = courseid).all()
    ttrs_all = []
    for task in tasks:
        ##team = Team.query.filter_by(course_id = task.course_id).first()
        ttrs = TaskTeamRelation.query.filter_by(task_id = task.id).all()
        if ttrs is not None:
            ttrs_all.extend(ttrs)

    teams = Team.query.filter_by(course_id = courseid).all()
    return render_template('teacher/multi_check.html',ttrs_all = ttrs_all,courseid = courseid,tasks = tasks,teams = teams)

@blueprint.route('/<courseid>/task/submit/download')
def task_check_download(courseid):
    book = xlwt.Workbook()
    tasklist = Task.query.filter_by(course_id=courseid).all()

    ttrs_all = []
    for task in tasklist:
        ttrs = TaskTeamRelation.query.filter_by(task_id = task.id).all()
        if ttrs is not None:
            ttrs_all.extend(ttrs)
    teamlist = Team.query.filter_by(course_id = courseid).all()
    ##tasks = Task.query.filter_by(course_id=courseid).all()
    alignment = xlwt.Alignment()  # Create Alignment
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle()  # Create Style
    style.alignment = alignment  # Add Alignment to Style

    sheet1 = book.add_sheet('作业信息', cell_overwrite_ok=True)
    row0 = ['团队id', '团队名称']
    for task in tasklist:
        row0.append(task.name)

    for i in range(0, len(row0)):
        sheet1.write(0, i, row0[i])

    row_num = 1

    for team in teamlist:
        ##turs = TeamUserRelation.query.filter_by(team_id=team.id).all()
        i = 2
        sheet1.write(row_num, 0 , team.id)
        sheet1.write(row_num, 1, team.name)
        for ttrs in ttrs_all:
            if ttrs.team_id == team.id:
                sheet1.write(row_num, i , ttrs.score)
                i = i+1
        ##row_num = row_num + turs_length
        row_num = row_num + 1

    filename = 'task_check_table_' + str(time.time()) + '.xls'
    book.save(os.path.join(data_uploader.path('', folder='tmp'), filename))
    return send_from_directory(data_uploader.path('', folder='tmp'), filename, as_attachment=True)



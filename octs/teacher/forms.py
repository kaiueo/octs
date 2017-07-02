from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField,DateTimeField,TextAreaField, FileField
from wtforms.validators import DataRequired, InputRequired
# coding=utf-8

class CourseForm(Form):
    coursename = StringField('名称')
    credit = FloatField('学分')
    location = StringField('地点')
    start_time = DateField('开始时间')
    course_introduction = TextAreaField('课程介绍')
    course_outline = TextAreaField("课程大纲")
    submit = SubmitField('提交')

class TaskForm(Form):
    taskname = StringField('名称')
    starttime = DateTimeField('开始时间')
    endtime = DateTimeField('结束时间')
    subnum = FloatField('可提交次数')
    content = TextAreaField('内容')
    submit = SubmitField('提交')

class FileForm(Form):
    file = FileField('图片上传', validators=[DataRequired('请选择文件')])
    submit = SubmitField('上传')

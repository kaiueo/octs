from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField,DateTimeField,TextAreaField, FileField
from wtforms.validators import DataRequired, InputRequired,NumberRange
# coding=utf-8

class CourseForm(Form):
    coursename = StringField('名称')
    credit = FloatField('学分')
    location = StringField('地点')
    start_time = DateField('开始时间')
    course_introduction = TextAreaField('课程介绍')
    course_outline = TextAreaField("课程大纲")
    low_member = FloatField('团队下限',validators=[NumberRange(1,10)])
    high_member = FloatField('团队上限',validators=[NumberRange(1,20)])
    submit = SubmitField('提交')

class TaskForm(Form):
    taskname = StringField('名称')
    starttime = DateTimeField('开始时间')
    endtime = DateTimeField('结束时间')
    subnum = FloatField('可提交次数',validators=[NumberRange(1,10)])
    content = TextAreaField('内容')
    weight = FloatField('作业权重',validators=[NumberRange(1,3)])
    submit = SubmitField('提交')

class FileForm(Form):
    file = FileField('图片上传', validators=[DataRequired('请选择文件')])
    submit = SubmitField('上传')

class TaskScoreForm(Form):
    task_score=FloatField('分数')
    submit = SubmitField('提交')

class RejectReasonForm(Form):
    content = TextAreaField('内容',validators=[DataRequired('请填写理由')])
    submit = SubmitField('提交')
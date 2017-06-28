from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class CourseForm(Form):
    coursename = StringField('名称')
    credit = FloatField('学分')
    location = StringField('地点')
    start_time = DateField('开始时间')
    course_introduction = StringField('课程介绍')
    course_outline = StringField("课程大纲")
    submit = SubmitField('查看')
class TeamRequireForm(Form):
    submit=SubmitField('提交')
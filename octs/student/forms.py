from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField,FileField, FieldList
from wtforms.validators import DataRequired, Email, EqualTo, Length
from octs.database import Column, Model, SurrogatePK, db, reference_col, relationship
from octs.user.models import Team

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

class TeamForm(Form):
    teamname = StringField('团队名称',validators=[DataRequired()])
    submit = SubmitField('提交')

class FileForm(Form):
    file = FileField('附件下载', validators=[DataRequired('请选择文件')])
    submit = SubmitField('下载')

class FileUploadForm(Form):
    file = FileField('文件', validators=[DataRequired('请选择文件')])
    submit = SubmitField('上传')



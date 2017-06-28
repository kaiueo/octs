from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from octs.database import Column, Model, SurrogatePK, db, reference_col, relationship
from octs.user.models import Term
# -*- coding: UTF-8 -*-
class CourseForm(Form):
    coursename = StringField('名称',validators=[DataRequired()])
    credit = FloatField('学分',validators=[DataRequired()])
    location = StringField('地点',validators=[DataRequired()])
    course_introduction = StringField('课程介绍',validators=[DataRequired()])
    start_time = DateField('开始时间',validators=[DataRequired()])
    submit = SubmitField('Submit')

class TermForm(Form):
    termname = StringField('名称',validators=[DataRequired()])
    week_number = FloatField('周次',validators=[DataRequired()])
    start_time = DateField('开始时间', validators=[DataRequired()])
    end_time = DateField('结束时间', validators=[DataRequired()])
    submit = SubmitField('提交')
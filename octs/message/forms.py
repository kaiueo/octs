from flask_wtf import Form
from wtforms import PasswordField, StringField,SubmitField,FloatField,DateField,FileField, FieldList, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class MessageForm(Form):
    send_to = StringField('收信人学号/工号', validators=[DataRequired()])
    title = StringField('标题', validators=[DataRequired()])
    message = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发送')
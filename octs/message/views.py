from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course, Message, User
from octs.database import db
from .forms import MessageForm
from flask_login import current_user

blueprint = Blueprint('message', __name__, url_prefix='/message',static_folder='../static')

@blueprint.route('/all/<id>')
def show_all(id):
    messages = Message.query.filter_by(to_id=id).all()
    usernames = []
    for message in messages:
        from_id = message.from_id
        user = User.query.filter_by(id=from_id).first()
        usernames.append(user.name)
    length = len(messages)
    return render_template('message/list.html', length=length, messages=messages, names=usernames, listtype='全部消息')

@blueprint.route('/unread/<id>')
def show_unread(id):
    messages = Message.query.filter_by(to_id=id).all()
    messages = [message for message in messages if message.has_read==False]
    usernames = []
    for message in messages:
        from_id = message.from_id
        user = User.query.filter_by(id=from_id).first()
        usernames.append(user.name)
    length = len(messages)
    return render_template('message/list.html', length=length, messages=messages, names=usernames, listtype='未读消息')

@blueprint.route('/detail/<id>')
def show_detail(id):
    message = Message.query.filter_by(id=id).first()
    message.has_read = True
    db.session.add(message)
    db.session.commit()
    user = User.query.filter_by(id=message.from_id).first()
    return render_template('message/detail.html', message=message, name=user.name)

@blueprint.route('/send/', methods=['GET', 'POST'])
def send():
    form = MessageForm()
    if form.validate_on_submit():
        to_user_id = form.send_to.data
        user = User.query.filter_by(user_id=to_user_id).first()
        if user is None:
            flash('该用户不存在')
            return redirect(url_for('message.send'))
        title = form.title.data
        message = form.message.data
        Message.sendMessage(current_user.id, user.id, message=message, title=title)
        flash('消息发送成功')
        return redirect(url_for('message.send'))
    return render_template('message/send_message.html', form=form)


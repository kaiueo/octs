from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course, Message, User
from octs.database import db

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
    return render_template('message/list.html', length=length, messages=messages, names=usernames)

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
    return render_template('message/list.html', length=length, messages=messages, names=usernames)

@blueprint.route('/detail/<id>')
def show_detail(id):
    message = Message.query.filter_by(id=id).first()
    message.has_read = True
    db.session.add(message)
    db.session.commit()
    user = User.query.filter_by(id=message.from_id).first()
    return render_template('message/detail.html', message=message, name=user.name)

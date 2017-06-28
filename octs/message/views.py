from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course, Message, User
from octs.database import db

blueprint = Blueprint('message', __name__, url_prefix='/message',static_folder='../static')

@blueprint.route('/<id>')
def show_all(id):
    messages = Message.query.filter_by(to_id=id).all()
    usernames = []
    for message in messages:
        from_id = message.from_id
        user = User.query.filter_by(id=from_id).first()
        usernames.append(user.name)
    length = len(messages)
    return render_template('message/unread.html', length=length, messages=messages, names=usernames)

@blueprint.route('/<id>')
def show_unread(id):
    messages = Message.query.filter_by(to_id=id).all()
    messages = [message for message in messages if message.has_read==False]
    usernames = []
    for message in messages:
        from_id = message.from_id
        user = User.query.filter_by(id=from_id).first()
        usernames.append(user.name)
    length = len(messages)
    return render_template('message/unread.html', length=length, messages=messages, names=usernames)

from flask import Blueprint, flash, redirect, render_template, request, url_for,sessions
from octs.user.models import Course, Message
from octs.database import db

blueprint = Blueprint('message', __name__, url_prefix='/message',static_folder='../static')

@blueprint.route('/<id>')
def show_all(id):
    messages = Message.query.filter_by(to_id=id)
    return render_template()
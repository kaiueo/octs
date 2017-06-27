from flask import Blueprint, flash, redirect, render_template, request, url_for
from octs.user.models import Term

blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('admin/index.html')
@blueprint.route('/term')
def term():
    termList = Term.query.order_by(Term.start_time).all()
    return render_template('admin/term.html', list=termList)
@blueprint.route('/term/add')
def term_add():

    return render_template('admin/term/add.html')
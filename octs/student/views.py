from flask import Blueprint, flash, redirect, render_template, request, url_for

blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('student/index.html')
@blueprint.route('/team')
def team():
    return render_template('student/team.html')
@blueprint.route('/team/create')
def create_team():
    return render_template('student/team/create.html')
@blueprint.route('/team/myTeam')
def my_team():
    return render_template('student/team/myTeam.html')
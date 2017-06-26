from flask import Blueprint, flash, redirect, render_template, request, url_for

blueprint = Blueprint('student', __name__, url_prefix='/student',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('teacher/index.html')

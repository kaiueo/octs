from flask import Blueprint, flash, redirect, render_template, request, url_for

blueprint = Blueprint('admin', __name__, url_prefix='/admin',static_folder='../static')

@blueprint.route('/')
def home():
    return render_template('admin/index.html')
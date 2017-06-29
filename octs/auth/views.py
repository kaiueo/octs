# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from octs.extensions import login_manager
from octs.auth.forms import LoginForm
from octs.user.forms import RegisterForm
from octs.user.models import User
from octs.utils import flash_errors

blueprint = Blueprint('auth', __name__, url_prefix='/auth',static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """Home page."""
    form = LoginForm()
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.check_password(form.password.data):
                login_user(user)
                flash('You are logged in.', 'success')
                redirect_url = request.args.get('next') or url_for('public.home')
                return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('login.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)

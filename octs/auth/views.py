# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from octs.database import db
from octs.extensions import login_manager
from octs.auth.forms import LoginForm
from octs.user.forms import RegisterForm
from .forms import PasswordForm
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
                flash('您已成功登陆', 'success')
                redirect_url = url_for('public.home')
                return redirect(redirect_url)
            else:
                flash('请输入正确的账号和密码', 'failed')
    return render_template('login.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('public.home'))

@blueprint.route('/password', methods=['GET', 'POST'])
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        if current_user.check_password(old_password):
            new_password = form.new_password.data
            current_user.set_password(new_password)
            db.session.add(current_user)
            db.session.commit()
            flash('修改成功')
            return redirect(url_for('public.home'))
        else:
            flash('密码错误')
            return redirect(url_for('auth.change_password'))
    return render_template('auth/change_password.html', form=form)



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

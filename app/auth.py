import functools
import ldap

from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db, login_manager
from app.models import User
from app.forms import LoginForm


bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('vote.ballot'))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            if not app.config['DEBUG']:
                User.try_login(form.username.data, form.password.data)
        except ldap.INVALID_CREDENTIALS:
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html', form=form)
        except ldap.SERVER_DOWN:
            flash('Could not connect to the LDAP server.', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            user = User(form.username.data)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('You have successfully logged in!', 'success')
        return redirect(url_for('vote.ballot'))

    if form.errors:
        if isinstance(form.errors, dict):
            flash(form.errors.values()[0][0], 'danger')

    return render_template('auth/login.html', form=form)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

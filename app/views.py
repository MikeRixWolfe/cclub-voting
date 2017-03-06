import ldap
from flask import request, render_template, flash, redirect, \
    url_for, Blueprint, Response, g
from flask.ext.login import current_user, login_user, \
    login_required
from sqlalchemy.sql import func
from app import app, db, login_manager
from app.models import User, Vote, Ballot
from app.forms import LoginForm, BallotForm


auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def get_current_user():
    g.user = current_user


@app.before_request
def load_application_data():
    nominees = ",".join(sorted(app.config['NOMINEES_CSV'].split(',')))

    _ballot = Ballot.query.filter_by(nominees=nominees).first()
    if not _ballot:
        _ballot = Ballot(nominees)
        db.session.add(_ballot)
        db.session.commit()

    g.nominees = _ballot.nominees.split(',')
    g.ballot_id = _ballot.id


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('ballot'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            User.try_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash('Invalid username or password. Please try again.',
                  'danger')
            return render_template('login.html', form=form)
        except ldap.SERVER_DOWN:
            flash('Could not connect to the LDAP server. Please try again later.',
                  'danger')
            return render_template('login.html', form=form)

        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('ballot'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@app.route('/ballot', strict_slashes=False, methods=['GET','POST'])
def ballot():
    if not current_user.is_authenticated:
        flash('You must be logged in.')
        return redirect(url_for('login'))

    if db.session.query(Vote).filter(Vote.user==g.user.username). \
                             filter(Vote.ballot==g.ballot_id).all():
        flash('You have already voted!', 'success')
        return redirect(url_for('results'))

    nominees = g.nominees
    form = BallotForm()
    if form.validate_on_submit():
        nominees = form.nomineesHidden.data.split(',')
        votes = {nominee: len(nominees) - nominees.index(nominee)
                 for nominee in nominees}
        for vote in votes:
            new_vote = Vote(g.ballot_id, vote, votes[vote], g.user.username)
            db.session.add(new_vote)
        db.session.commit()
        flash('You have successfully voted!', 'success')
        return redirect(url_for('results'))
    return render_template('ballot.html', form=form,
                           nominees=nominees)


@app.route('/results', strict_slashes=False, methods=['GET'])
def results():
    # db stuff
    #total_votes = select count(distinct user) from vote where ballot = g.ballot_id
    #score_per_nom = select user, sum(score) from vote where ballot = g.ballot_id group by score

    total_votes = 123
    scores_per_nom = {'dolphin': 5, 'leech': 4, 'zurek': 3, 'sgtsarcasm': 2, 'mobyte': 1}
    return render_template('results.html', total_votes=total_votes,
                           scores_per_nom=scores_per_nom)


@app.route('/static/js/<script_file>')
def script_helper(script_file):
    with open('app/static/js/{}'.format(script_file), "r") as f:
        script = f.readlines()
    return Response(script, mimetype='application/json')


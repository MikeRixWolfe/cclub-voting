import json
import ldap
from datetime import date
from flask import request, render_template, flash, redirect, \
    url_for, Blueprint, Response, g
from flask.ext.login import current_user, login_user, \
    logout_user, login_required
from sqlalchemy.sql import func
from app import app, db, login_manager
from app.models import User, Vote, Ballot
from app.forms import LoginForm, BallotForm
from app.util import irv


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


@app.route('/login', strict_slashes=False, methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('ballot'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form.get('username').lower()
        password = request.form.get('password')

        try:
            if not app.config['DEBUG']:
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
        flash('You have successfully logged in!', 'success')
        return redirect(url_for('ballot'))

    if form.errors:
        if isinstance(form.errors, dict):
            flash(form.errors.values()[0][0], 'danger')

    return render_template('login.html', form=form, year=date.today().year)


@app.route('/ballot', strict_slashes=False, methods=['GET','POST'])
def ballot():
    if not current_user.is_authenticated:
        flash('You must be logged in.', 'warning')
        return redirect(url_for('login'))

    form = BallotForm()
    _votes = db.session.query(Vote.id).filter(Vote.user==g.user.username). \
            filter(Vote.ballot==g.ballot_id)

    if form.validate_on_submit():
        nominees = form.nomineesHidden.data.split(',')
        if set(nominees) != set(g.nominees):
            flash('Submitted votes do not match available nomiees.', 'danger')
            return render_template('ballot.html', form=form, nominees=g.nominees,
                                   revote=bool(_votes.first()))

        if _votes.first():
            _votes.delete()
            db.session.commit()

        votes = {nominee: len(nominees) - nominees.index(nominee)
                 for nominee in nominees}

        for vote in votes:
            new_vote = Vote(g.ballot_id, vote, votes[vote], g.user.username)
            db.session.add(new_vote)

        db.session.commit()
        flash('You have successfully voted!', 'success')
        return redirect(url_for('results'))

    if _votes.first():
        flash('{} has already voted, if you vote again your old votes will ' \
              'be overwritten.'.format(g.user.username.title()), 'warning')

    return render_template('ballot.html', form=form, nominees=g.nominees,
                           revote=bool(_votes.first()))


@app.route('/get_results', strict_slashes=False, methods=['GET'])
def get_results():
    total_votes = Vote.query.filter_by(ballot=g.ballot_id). \
                  distinct(Vote.user).group_by(Vote.user).count()
    scores_per_nom = db.session.query(Vote.nominee, func.sum(Vote.score)). \
                     filter_by(ballot=g.ballot_id).group_by(Vote.nominee). \
                     order_by(func.sum(Vote.score)).all()

    backgroundColors = ['#ff0000','#ff8000','#ffff00','#40ff00','#00ffff',
                        '#0040ff','#0000ff','#8000ff','#ff00ff','#95a5a6']
    pieData = {'datasets': [{'data': [], 'backgroundColor': [], 'label': 'Results'}],
               'labels': []}

    if not scores_per_nom:
        scores_per_nom = [('No one', 1)]
        winner = 'No one'
    else:
        winner = ", ".join(['{} (with {}%)'.format(k, round(v, 3)*100)
                           for k,v in irv(g.ballot_id, g.nominees).iteritems()])

    for ix, score in enumerate(scores_per_nom):
        pieData['datasets'][0]['data'].append(score[1])
        pieData['datasets'][0]['backgroundColor'].append(backgroundColors[ix])
        pieData['labels'].append(score[0])

    return json.dumps({'totalVotes': total_votes, 'pieData': pieData, 'winner': winner})


@app.route('/results', strict_slashes=False, methods=['GET'])
def results():
    return render_template('results.html')


@app.route('/logout', strict_slashes=False, methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

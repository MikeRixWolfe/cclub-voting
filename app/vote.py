from flask import render_template, flash, redirect, url_for, Blueprint, g
from flask_login import current_user, login_required
from json import dumps
from sqlalchemy.sql import func

from app import app, db, login_manager
from app.models import User, Vote, Ballot
from app.forms import BallotForm
from app.util import irv


bp = Blueprint('vote', __name__, url_prefix='/vote')


@bp.before_request
def load_application_data():
    nominees = ",".join(sorted(app.config['NOMINEES_CSV'].split(',')))
    _ballot = Ballot.query.filter_by(nominees=nominees).first()

    if not _ballot:
        _ballot = Ballot(nominees)
        db.session.add(_ballot)
        db.session.commit()

    g.nominees = _ballot.nominees.split(',')
    g.ballot_id = _ballot.id


@bp.route('/ballot', methods=['GET','POST'])
@login_required
def ballot():
    form = BallotForm()
    _votes = db.session.query(Vote.id).filter(Vote.user==current_user.username).filter(Vote.ballot==g.ballot_id)

    if form.validate_on_submit():
        nominees = form.nomineesHidden.data.split(',')
        if set(nominees) != set(g.nominees):
            flash('Submitted votes do not match available nomiees.', 'danger')
            return render_template('ballot.html', form=form, nominees=g.nominees,
                                   revote=bool(_votes.first()))

        if _votes.first():
            _votes.delete()
            db.session.commit()

        votes = {nominee: len(nominees)-nominees.index(nominee) for nominee in nominees}

        for vote in votes:
            new_vote = Vote(g.ballot_id, vote, votes[vote], current_user.username)
            db.session.add(new_vote)

        db.session.commit()
        flash('You have successfully voted!', 'success')
        return redirect(url_for('vote.results'))

    if _votes.first():
        flash('Revoting will overwrite previous votes.', 'warning')

    return render_template('vote/ballot.html', form=form, nominees=g.nominees,
                           revote=bool(_votes.first()))


@bp.route('/get_results', methods=['GET'])
def get_results():
    total_votes = Vote.query.filter_by(ballot=g.ballot_id).distinct(Vote.user).group_by(Vote.user).count()
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

    return dumps({'totalVotes': total_votes, 'pieData': pieData, 'winner': winner})


@bp.route('/results', methods=['GET'])
def results():
    return render_template('vote/results.html')


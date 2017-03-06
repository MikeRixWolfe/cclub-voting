from datetime import date
from flask import render_template, flash, redirect, request, Response
from app import app
from .forms import BallotForm#, LoginForm
from .util import getData


#@app.route('/login', strict_slashes=False, methods=['GET','POST'])
def index2():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Logging in {} with LDAP'.format(form.uname.data))
        return redirect('ballot')

    return render_template('login.html',
                           form=form)


@app.route('/ballot', strict_slashes=False, methods=['GET','POST'])
def ballot():
    nominees = ['dolphin', 'leech', 'zurek', 'sgtsarcasm', 'mobyte']

    form = BallotForm()
    if form.validate_on_submit():
        # record nominees
        print(form.nomineesHidden.data)
        return redirect('results')
    return render_template('ballot.html',
                           form=form,
                           nominees=nominees)


@app.route('/results', strict_slashes=False, methods=['GET'])
def results():
    # db stuff
    results = {'dolphin': 5, 'leech': 4, 'zurek': 3, 'sgtsarcasm': 2, 'mobyte': 1}
    return render_template('results.html',
                            results=results)


@app.route('/static/js/<script_file>')
def script_helper(script_file):
    with open('app/static/js/{}'.format(script_file), "r") as f:
        script = f.readlines()
    return Response(script,
                    mimetype='application/json')

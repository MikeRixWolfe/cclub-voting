import ldap
from datetime import datetime
from app import db, app


def get_ldap_connection():
    conn = ldap.initialize(app.config['LDAP_PROVIDER_URL'])
    return conn


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))

    def __init__(self, username):
        self.username = username

    @staticmethod
    def try_login(username, password):
        conn = get_ldap_connection()
        conn.simple_bind_s(
            'uid={},{}'.format(username,
            app.config['LDAP_DIRECTORY_STRING']),
            password
        )

    def is_authenticated(self):
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Ballot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nominees = db.Column(db.String(255))

    def __init__(self, nominees):
        self.nominees = nominees


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ballot = db.Column(db.Integer)
    user = db.Column(db.String(100))
    nominee = db.Column(db.String(100))
    score = db.Column(db.Integer)

    def __init__(self, ballot, nominee, score, user):
        self.ballot = ballot
        self.nominee = nominee
        self.score = score
        self.user = user


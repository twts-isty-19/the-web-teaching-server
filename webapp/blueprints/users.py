import os
import base64

import settings
import flask
from flask_mail import Mail, Message
import flask_login
import flask_mail
from flask.blueprints import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import sqlalchemy

from database import db

app = flask.Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', '12345')
app.config.update({
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': os.getenv(
        'DB_URI',
        'sqlite:///db.sqlite',
    ),
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': os.getenv('MAIL_PORT', 465),
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': True,
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME', 'foo@gmail.com'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD', '12345'),
    'SERVER_NAME': os.getenv('SERVER_NAME'),
})


mail = flask_mail.Mail(app)

users = Blueprint(
    'users',
    __name__,
    template_folder='templates',
    static_folder='static',
)

class User(flask_login.UserMixin, db.Model):
    __tablename__ = "users"
    email = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    is_teacher = db.Column(db.Boolean, default=False)
    token_for_register=db.Column(db.Text)
    password_hash = db.Column(db.Text)

    def get_id(self):
        return self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def create_users(names_emails, mailer):
    for name, email in names_emails:
        token = base64.urlsafe_b64encode(os.urandom(51)).decode()
        user = User(
            name=name,
            email=email,
            token_for_register=token,
        )

        db.session.add(user)
        try:
            db.session.commit()
            mailer.send_message(
                subject='Your account on "The Learning Web Server"',
                body="""Hello %s,
    An account has been created for you on the website %s . Follow the
    previous link to define your password!
                """%(
                    name,
                    flask.url_for('users.redefine_password', email=email, token=token),
                ),
                sender=settings.MAIL_DEFAULT_SENDER,
                recipients=[email],
            )
        except IntegrityError:
            db.session.rollback()



@users.route('/forgot_password/')
def forgot_password():
    return flask.render_template('forgotten-password.html')

  
@users.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
  
   email = flask.request.form.get('email')
   user = User.query.get(email)  

   redir_home = flask.redirect(flask.url_for('home'))
    
   if user is None:
        flask.flash("Something went wrong...")
        return redir_home
   else:
    mail.send_message(subject='Redefine your password !',
                     body="""Hello,
                      to redefine your password click on this link %s!
                      """%(flask.url_for('users.redefine_password',email=email,token=user),)
                      ,sender=settings.MAIL_DEFAULT_SENDER
                      ,recipients=[email],)
    flask.flash("Check your email box!")
    return redir_home


@users.route('/redefine_password/<email>/<token>', methods=['GET', 'POST'])
def redefine_password(email, token):
    user = User.query.get(email)

    redir_home = flask.redirect(flask.url_for('home'))
    if user is None or user.token_for_register != token:
        flask.flash("Something went wrong...")
        return redir_home

    if flask.request.method == 'GET':
        return flask.render_template('redefine_password.html', name=user.name)

    # POST method assumed here:
    password1 = flask.request.form.get('password1')
    password2 = flask.request.form.get('password2')

    if password1 is None or password2 is None:
        flask.flash("Please fulfill the two password fields")
        return flask.render_template('redefine_password.html', name=user.name)

    if password1 != password2:
        flask.flash("The passwords did not match")
        return flask.render_template('redefine_password.html', name=user.name)

    user.set_password(password1)
    user.token_for_register = None
    db.session.commit()

    remember = flask.request.form.get('remember_me')
    flask_login.login_user(user, remember=remember)
    return redir_home


@users.route('/login', methods=['POST'])
def login_post():
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    remember = flask.request.form.get('remember_me')
    if not email or not password:
        flask.flash("Please provide your email and your password.")
        return flask.redirect(flask.url_for('users.login_get'))


    user = User.query.filter(sqlalchemy.func.lower(User.email) == sqlalchemy.func.lower(email)).first()
    if user is None or not user.check_password(password):
        flask.flash("Authentication failed")
        return flask.redirect(flask.url_for('users.login_get'))


    flask_login.login_user(user, remember=remember)
    flask.flash("Logged in as %s!" % email)
    return flask.redirect(flask.url_for('home'))

@users.route('/login', methods=['GET'])
def login_get():
    return flask.render_template('login.html')

@users.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('users.login_get'))

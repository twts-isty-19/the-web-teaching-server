import os

import flask
import flask_login
from flask_sqlalchemy import SQLAlchemy
from jinja2.exceptions import TemplateNotFound
from werkzeug.security import generate_password_hash, check_password_hash

app = flask.Flask(__name__)
app.secret_key = os.urandom(50)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DB_URI',
    'sqlite:///db.sqlite',
)
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_get'

class User(flask_login.UserMixin, db.Model):
    __tablename__ = "users"
    email = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    password_hash = db.Column(db.Text)

    def get_id(self):
        return self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

login_manager.user_loader(User.query.get)

class Chapter(db.Model):
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    end_date = db.Column(db.Date)


@app.route('/')
@flask_login.login_required
def home():
    return flask.render_template('home.html', chapters=Chapter.query.all())

@app.route('/login', methods=['POST'])
def login_post():
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    remember = flask.request.form.get('remember_me')
    if not email or not password:
        flask.flash("Entrez un nom d'utilisateur et un mot de passe")
        return flask.redirect(flask.url_for('login_get'))


    user = User.query.get(email)
    if user is None or not user.check_password(password):
        flask.flash("Identifiants invalides")
        return falsk.redirect(flask.url_for('login_get'))

    flask_login.login_user(user, remember=remember)
    flask.flash("Identifié en tant que %s!" % email)
    return flask.redirect(flask.url_for('home'))

@app.route('/login', methods=['GET'])
def login_get():
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    flask_login.logout()
    return flask.redirect(flask.url_for('login_get'))


@app.route('/chapter/<chapter_id>')
#@flask_login.login_required
def chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return render_error(
            "La route %s n'existe pas !"%flask.request.path
        )

    try:
        return flask.render_template('lessons/%s.html'%chapter_id)
    except TemplateNotFound:
        return render_error(
            "La leçon n'est pas encore écrite ! Revenez plus tard."
        )

def render_error(message):
    return flask.render_template(
        'error.html',
        message=message,
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.getenv('DEBUG', False))

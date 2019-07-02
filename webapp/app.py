import os

import flask
import flask_login
import flask_mail

import blueprints.lessons as lessons_module
import blueprints.users as users_module
import blueprints.answers as answers_module

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


db.init_app(app)
app.register_blueprint(lessons_module.lessons)
app.register_blueprint(users_module.users)
app.register_blueprint(answers_module.answers)

mail = flask_mail.Mail(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login_get'

with app.app_context():
    login_manager.user_loader(users_module.User.query.get)

@app.route('/')
@flask_login.login_required
def home():
    chapters = lessons_module.Chapter.query.all()
    answers = answers_module.Answers.query.filter_by(user_id=flask_login.current_user.get_id())
    for chapter in chapters:
        chapter.quizz_status = answers_module.quizz_status(answers, chapter)
    return flask.render_template('home.html', chapters=chapters)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.getenv('DEBUG', False))

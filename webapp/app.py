import os

import flask
import flask_login
import flask_mail

import blueprints.lessons as lessons_module
import blueprints.chapter_http as chapter_http_module
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
app.register_blueprint(users_module.users)
app.register_blueprint(lessons_module.lessons)
app.register_blueprint(answers_module.answers)
app.register_blueprint(chapter_http_module.chapter_http)

mail = flask_mail.Mail(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login_get'

with app.app_context():
    login_manager.user_loader(users_module.User.query.get)

@app.route('/')
@flask_login.login_required
def home():
    chapters = sorted(lessons_module.Chapter.query.all(), key=lambda c: c.id)
    user = flask_login.current_user

    for chapter in chapters:
        if chapter.id == chapter_http_module.CHAPTER_ID:
            chapter.quizz_status = chapter_http_module.quizz_status(user)
        else:
            chapter.quizz_status = answers_module.quizz_status(
                chapter,
                user,
            )
        score, max = answers_module.compute_score(chapter,user)
    return flask.render_template('home.html', chapters=chapters, score=score, max=max)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.getenv('DEBUG', False))

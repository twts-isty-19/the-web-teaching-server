import os


import flask
import flask_login
import flask_mail

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

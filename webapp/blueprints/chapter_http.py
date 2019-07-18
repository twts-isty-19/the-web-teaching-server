import flask
import flask_login
from database import db

from flask.blueprints import Blueprint
import blueprints.lessons as lessons
from datetime import datetime

CHAPTER_ID = "03-HTTP"

NUMBER_OF_VISITS = 1000


chapter_http = Blueprint(
    'chapter_http',
    __name__,
    template_folder='templates',
    static_folder='static',
)


class AnswerForHttp(db.Model):
    user_id = db.Column(db.Text, db.ForeignKey('users.email', ondelete="CASCADE"), primary_key=True)
    challenge_param = db.Column(db.Boolean, default=False)
    challenge_get = db.Column(db.Boolean, default=False)
    challenge_post = db.Column(db.Boolean, default=False)
    challenge_repeat = db.Column(db.Integer, default=0)
    challenge_content_type = db.Column(db.Boolean, default=False)

    QUESTION_COUNT = 5

    def nb_answered(self):
        res = 0

        if self.challenge_param:
            res += 1

        if self.challenge_get:
            res += 1

        if self.challenge_post:
            res += 1

        if self.challenge_repeat >= NUMBER_OF_VISITS:
            res += 1

        if self.challenge_content_type:
            res += 1

        return res


    @classmethod
    def get_or_create(cls, user_id):
        answer = cls.query.get(user_id)
        if answer is None:
            answer = cls(user_id=user_id)
            db.session.add(answer)
        return answer


def get_dead_line():
    chapter = lessons.Chapter.query.get(CHAPTER_ID)
    return chapter.end_date

def quizz_status(user):
    answer_object = AnswerForHttp.query.get(user.get_id())
    if answer_object is None:
        res = "Not started"
    else:
        res = "%d/%d" % (
          answer_object.nb_answered(),
          answer_object.QUESTION_COUNT,
        )

    if get_dead_line() < datetime.now().date():
        res += " - Deadline exceeded"

    return res


# This route will override the one in answers.py
@chapter_http.route('/quizz/' + CHAPTER_ID)
@flask_login.login_required
def render_quizz():
    user = flask_login.current_user
    answer_object = AnswerForHttp.query.get(user.get_id())

    return flask.render_template(
        'lessons/03-HTTP/quizz.html',
        challenge_param=answer_object.challenge_param,
        challenge_get=answer_object.challenge_get,
        challenge_post=answer_object.challenge_post,
        challenge_repeat=answer_object.challenge_repeat >= NUMBER_OF_VISITS,
        challenge_content_type=answer_object.challenge_content_type,
    )


@chapter_http.route('/http-challenge-param/')
@chapter_http.route('/http-challenge-param/<int:visit_count>')
@flask_login.login_required
def challenge_param(visit_count=1):
    if get_dead_line() < datetime.now().date():
        return "Deadline exceeded for this challenge!"

    if visit_count >= NUMBER_OF_VISITS:
        answer = AnswerForHttp.get_or_create(flask_login.current_user.get_id())
        answer.challenge_param = True
        db.session.commit()
        return flask.render_template(
            'lessons/03-HTTP/challenge-param.html',
            message="Congrats! You have reached the %d-th visit!"% NUMBER_OF_VISITS,
            count=visit_count,
        )

    return  flask.render_template(
        'lessons/03-HTTP/challenge-param.html',
        message="Visit this page %d times to meet this challenge!"% NUMBER_OF_VISITS,
        count=visit_count,
    )


@chapter_http.route('/http-challenge-get/')
@flask_login.login_required
def challenge_get():
    if get_dead_line() < datetime.now().date():
        return "Deadline exceeded for this challenge!"

    visit_count = flask.request.args.get('count', 1)
    try:
        visit_count = int(visit_count)
    except ValueError:
        visit_count = 1

    if visit_count >= NUMBER_OF_VISITS:
        answer = AnswerForHttp.get_or_create(flask_login.current_user.get_id())
        answer.challenge_get = True
        db.session.commit()
        return flask.render_template(
            'lessons/03-HTTP/challenge-get.html',
            message="Congrats! You have reached the %d-th visit!"% NUMBER_OF_VISITS,
            count=visit_count,
        )

    return  flask.render_template(
        'lessons/03-HTTP/challenge-get.html',
        message="Visit this page %d times to meet this challenge!"% NUMBER_OF_VISITS,
        count=visit_count,
    )

@chapter_http.route('/http-challenge-post/', methods=['GET', 'POST'])
@flask_login.login_required
def challenge_post():
    if get_dead_line() < datetime.now().date():
        return "Deadline exceeded for this challenge!"

    if flask.request.method == 'GET':
        visit_count = 1
    else:
        visit_count = flask.request.form.get('count', 1)
        try:
            visit_count = int(visit_count)
        except ValueError:
            visit_count = 1

    if visit_count >= NUMBER_OF_VISITS:
        answer = AnswerForHttp.get_or_create(flask_login.current_user.get_id())
        answer.challenge_post = True
        db.session.commit()
        return flask.render_template(
            'lessons/03-HTTP/challenge-post.html',
            message="Congrats! You have reached the %d-th visit!"% NUMBER_OF_VISITS,
            count=visit_count,
        )

    return  flask.render_template(
        'lessons/03-HTTP/challenge-post.html',
        message="Visit this page %d times to meet this challenge!"% NUMBER_OF_VISITS,
        count=visit_count,
    )


@chapter_http.route('/http-challenge-repeat/')
@flask_login.login_required
def challenge_repeat():
    if get_dead_line() < datetime.now().date():
        return "Deadline exceeded for this challenge!"

    answer = AnswerForHttp.get_or_create(flask_login.current_user.get_id())

    visit_count = answer.challenge_repeat
    if visit_count is None:
        visit_count = 0
    visit_count += 1
    answer.challenge_repeat = visit_count
    db.session.commit()

    if visit_count >= NUMBER_OF_VISITS:
        return flask.render_template(
            'lessons/03-HTTP/challenge-repeat.html',
            message="Congrats! You have reached the %d-th visit!"% NUMBER_OF_VISITS,
            count=visit_count,
        )

    return  flask.render_template(
        'lessons/03-HTTP/challenge-repeat.html',
        message="Visit this page %d times to meet this challenge. This time, "
        "you cannot cheat, you have to visit this page multiple times!"% NUMBER_OF_VISITS,
        count=visit_count,
    )


@chapter_http.route('/http-challenge-content-type/')
@flask_login.login_required
def challenge_content_type():
    if get_dead_line() < datetime.now().date():
        return "Deadline exceeded for this challenge!"

    if flask.request.content_type == 'application/json':
        answer = AnswerForHttp.get_or_create(flask_login.current_user.get_id())
        answer.challenge_content_type = True
        db.session.commit()
        return flask.jsonify({
            "message": "Congrats, you have asked for JSON! You have met this challenge!",
            "answer": 42,
        })

    return  flask.render_template(
        'lessons/03-HTTP/challenge-content-type.html',

    )


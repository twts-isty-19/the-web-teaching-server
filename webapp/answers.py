import flask
import flask_login
from flask.blueprints import Blueprint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.exc import NoResultFound

import lessons
import users
from lessons import Chapter

from database import db

answers = Blueprint(
    'answers',
    __name__,
    template_folder='templates',
    static_folder='static',
)

class Answers(db.Model):
    chapter_id =db.Column(db.Text, db.ForeignKey('chapter.id'), primary_key=True)
    user_id = db.Column(db.Text, db.ForeignKey('users.email'), primary_key=True)
    answers = db.Column(JSON)

    def nb_answered(self):
        return len([
            a for a in self.answers['questions']
            if a['answer'] is not None
        ])


def build_answers(chapter):
    return {
        'chapter_name': chapter.name,
        'questions': [
            { 'title': q['title'],
              'answer': None,
            }
            for q in chapter.questions
        ],
        'current_question': 0,
    }

def get_by_chapter_id(answers, chapter_id):
    try:
        return next(a for a in answers if a.chapter_id == chapter_id)
    except StopIteration:
        raise ValueError("no such answer")


@answers.route('/exercises/<chapter_id>', methods=['GET'])
@flask_login.login_required
def answers_get(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.render_template(
            "error.html",
            message="The route %s does not exist!"%flask.request.path,
        )

    if flask.request.content_type != 'application/json':
        return flask.render_template('exercises.html', chapter_id=chapter_id)

    answers_object = Answers.query.get(
        (chapter_id,flask_login.current_user.get_id())
    )
    if answers_object is None:
        answers = build_answers(chapter)
    else:
        answers = answers_object.answers

    chapter_questions = [q['title'] for q in chapter.questions]
    answers_questions = [q['title'] for q in  answers['questions']]
    if  chapter_questions != answers_questions:
        anwsers = build_answers(chapter)

    return flask.jsonify(answers)

@answers.route('/exercises/<chapter_id>', methods=['POST'])
@flask_login.login_required
def answers_post(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.jsonify({"error": "chapter does not exist"}), 404

    chapter_questions = [q['title'] for q in chapter.questions]
    answers_questions = [q['title'] for q in  flask.request.json['questions']]
    if chapter_questions != answers_questions:
        return flask.jsonify({"error": "bad questions list"}), 400

    answers_object = Answers.query.get(
        (chapter_id,flask_login.current_user.get_id())
    )

    if answers_object is None:
        db.session.add(Answers(
            chapter_id=chapter_id,
            user_id=flask_login.current_user.get_id(),
            answers=flask.request.json,
        ))
    else:
        answers_object.answers = flask.request.json
    db.session.commit()
    return flask.jsonify({"status": "ok"})

















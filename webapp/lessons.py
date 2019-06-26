import flask
import flask_login
from flask.blueprints import Blueprint
from jinja2.exceptions import TemplateNotFound
from sqlalchemy.dialects.postgresql import JSON

from database import db

lessons = Blueprint(
    'lessons',
    __name__,
    template_folder='templates',
    static_folder='static',
)

class Chapter(db.Model):
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    end_date = db.Column(db.Date)
    questions = db.Column(JSON)


class FreeAnswerQuestion:
    def __init__(self, title, grade_by_answer, coefficient):
        """Grade has to be between 0 and 1"""
        self.title = title
        self.grade_by_answer = grade_by_answer
        self.coefficient = coefficient

    def grade(self, answer):
        return self.grade_by_answer.get(answer.strip())

    def has_answer(self, answer):
        return answer in self.grade_by_answer

    def to_dict(self):
        return {
            'title': self.title,
            'grade_by_answer': self.grade_by_answer,
            'coefficient': self.coefficient,
            'kind': 'FreeAnswerQuestion'
        }

    @classmethod
    def from_dict(cls, dict_):
        return cls(
            title=dict_['title'],
            grade_by_answer=dict_['grade_by_answer'],
            coefficient=dict_['coefficient'],
        )

class QuestionsList:
    kind_to_class = {
        'FreeAnswerQuestion': FreeAnswerQuestion,
    }

    def __init__(self, *args):
        self.questions = args

    def to_dicts(self):
        return [q.to_dict() for q in self.questions]

    @classmethod
    def from_dicts(cls, dicts):
        cls(*(
            cls.kind_to_class[d['kind']].from_dict(d)
            for d in dicts
        ))

    def __iter__(self):
        return self.questions



@lessons.route('/chapter/<chapter_id>')
@flask_login.login_required
def chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return render_error(
            "The route %s does not exist!"%flask.request.path
        )

    try:
        return flask.render_template('lessons/%s.html'%chapter_id)
    except TemplateNotFound:
        return render_error(
            "The lesson has not been written! Come back later!"
        )


def render_error(message):
    return flask.render_template(
        'error.html',
        message=message,
    ), 404

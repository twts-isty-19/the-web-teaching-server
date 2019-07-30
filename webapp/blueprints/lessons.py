import flask
import flask_login
from flask.blueprints import Blueprint
from jinja2.exceptions import TemplateNotFound

from database import db
import json

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
    questions = db.Column(db.Text)

    @property
    def questions_list(self):
        try:
            return self._questions_list
        except AttributeError:
            self._questions_list = QuestionsList.from_dicts(json.loads(self.questions))
            return self._questions_list

    @questions_list.setter
    def questions_list(self, questions_list):
        self.questions = json.dumps(questions_list.to_dicts())
        self._questions_list = questions_list

    def max_score(self):
        return sum(q.coefficient for q in self.questions_list)

class FreeAnswerQuestion:
    def __init__(self, title, grade_by_answer, coefficient):
        """Grade has to be an integer between 0 and 4"""
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
        }

    def __repr__(self):
        return "[FreeAnswerQuestion: " + self.title[:10] + ", grade_by_answer:" +str(self.grade_by_answer) +"]"

    @classmethod
    def from_dict(cls, dict_):
        return cls(
            title=dict_['title'],
            grade_by_answer=dict_['grade_by_answer'],
            coefficient=dict_['coefficient'],
        )


class QuestionsList:

    def __init__(self, *args):
        self.questions = args

    def to_dicts(self):
        return [q.to_dict() for q in self.questions]

    @classmethod
    def from_dicts(cls, dicts):
        return cls(*(
            FreeAnswerQuestion.from_dict(d)
            for d in dicts
        ))

    def __len__(self):
        return len(self.questions)

    def __iter__(self):
        return iter(self.questions)



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

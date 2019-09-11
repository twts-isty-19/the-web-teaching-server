import flask
import flask_login
from flask.blueprints import Blueprint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from collections import defaultdict

import colorsys
import blueprints.lessons as lessons
import blueprints.users as users
from blueprints.lessons import Chapter, QuestionsList
import blueprints.chapter_http as chapter_http
from database import db



answers = Blueprint(
    'answers',
    __name__,
    template_folder='templates',
    static_folder='static',
)

class Answers(db.Model):
    chapter_id =db.Column(db.Text, db.ForeignKey('chapter.id', ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Text, db.ForeignKey('users.email', ondelete="CASCADE"), primary_key=True)
    answers = db.Column(JSON)

    def nb_answered(self):
        return len([
            a for a in self.answers['questions']
            if a['answer']
        ])


def build_answers(chapter):
    return {
        'chapter_name': chapter.name,
        'questions': [
            { 'title': q.title,
              'answer': None,
            }
            for q in chapter.questions_list
        ],
        'current_question': 0,
    }

def quizz_status(chapter, user):
    answer_object = Answers.query.get(
        (chapter.id, user.get_id())
    )

    if answer_object is None:
        res = "Not started"
    else:
        res = "%d/%d" % (
          answer_object.nb_answered(),
          len(chapter.questions_list),
        )

    if chapter.end_date < datetime.now().date():
        res += " - Deadline exceeded"

    return res

def compute_score(chapter, user):
    if chapter.id == chapter_http.CHAPTER_ID:
        answer = chapter_http.AnswerForHttp.get_or_create(user.get_id())
        return answer.compute_score(), chapter_http.AnswerForHttp.MAX_SCORE

    answer_object = Answers.query.get((chapter.id, user.get_id()))
    questions = chapter.questions_list

    if answer_object is None:
        return 0., chapter.max_score()

    score = 0
    for question, answer in zip(questions, answer_object.answers['questions']):
        answer_text = answer['answer']
        grade = question.grade_by_answer.get(answer_text, 0)

        score += question.coefficient * grade / 4
    return score, chapter.max_score()



@answers.route('/quizz/<chapter_id>', methods=['GET'])
@flask_login.login_required
def answers_get(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.render_template(
            "error.html",
            message="The route %s does not exist!"%flask.request.path,
        )

    if flask.request.content_type != 'application/json':
        return flask.render_template('quizz.html', chapter_id=chapter_id)

    answers_object = Answers.query.get(
        (chapter_id,flask_login.current_user.get_id())
    )
    if answers_object is None:
        answers = build_answers(chapter)
    else:
        answers = answers_object.answers

    chapter_questions = [q.title for q in chapter.questions_list]
    answers_questions = [q['title'] for q in  answers['questions']]
    if  chapter_questions != answers_questions:
        answers = build_answers(chapter)

    return flask.jsonify(answers)

@answers.route('/quizz/<chapter_id>', methods=['POST'])
@flask_login.login_required
def answers_post(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.jsonify({"error": "chapter does not exist"}), 404

    if chapter.end_date < datetime.now().date():
        return flask.jsonify({"error": "deadline exceeded"}), 400

    chapter_questions = [q.title for q in chapter.questions_list]
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

@answers.route('/correct-quizz/<chapter_id>/', methods=['GET'])
@flask_login.login_required
def correct_quizz(chapter_id):
    if not flask_login.current_user.is_teacher:
        return flask.render_template('error.html', message="Not authorized"), 403

    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.render_template('error.html', message= "chapter does not exist"), 404

    return flask.render_template('correct-quizz.html', chapter_name=chapter.name)

@answers.route('/correct-quizz/<chapter_id>/questions/', methods=['GET'])
@flask_login.login_required
def get_questions(chapter_id):
    if not flask_login.current_user.is_teacher:
        return flask.jsonify({"error": "not authorized"}), 403

    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.jsonify({"error": "chapter does not exist"}), 404
    
    return questions_json(chapter)


@answers.route('/correct-quizz/<chapter_id>/mark-answer/', methods=['POST'])
@flask_login.login_required
def mark_answer(chapter_id):
    if not flask_login.current_user.is_teacher:
        return flask.jsonify({"error": "not authorized"}), 403

    chapter = Chapter.query.get(chapter_id)
    if chapter is None:
        return flask.jsonify({"error": "chapter does not exist"}), 404

    questions = chapter.questions_list
    questionNumber = flask.request.json['questionNumber']
    answer = flask.request.json['answer']
    mark = flask.request.json['mark']

    questions.questions[questionNumber].grade_by_answer[answer] = mark

    chapter.questions_list = questions
    db.session.commit()

    return questions_json(chapter)

def compute_color(score, max_score):
    ratio = score/max_score

    hue = 120 *  ratio / 360
    sat = 0.5 + abs(ratio - 0.5)
    val = 1

    (red, green, blue) = colorsys.hsv_to_rgb(hue, sat, val)
    return "rgb(%d, %d, %d)"%(red*255, green*255, blue*255)



@answers.route('/see-results/', methods=['GET'])
@flask_login.login_required
def see_results():
    if not flask_login.current_user.is_teacher:
        return flask.render_template("error.html", message= "not authorized"), 403

    userlist = users.User.query.order_by('email').all()
    chapters = Chapter.query.order_by('id').all()
    users_with_marks = []
    for u in userlist:
        marks = []
        for chapter in chapters:
            score, max_score = compute_score(chapter, u)
            color = compute_color(score, max_score)
            marks.append((score, max_score, color))

        users_with_marks.append({
            'email': u.email
            , 'name': u.name
            , 'marks': marks
            , 'total': sum(m[0] for m in marks)
            , 'total_max': sum(m[1] for m in marks)
        })

    return flask.render_template("results.html",
        users_with_marks=users_with_marks,
        chapters=chapters
    )


def questions_json(chapter):
    questions = chapter.questions_list
    answers_objects = Answers.query.filter_by(chapter_id=chapter.id).all()
    users_dict = { u.get_id(): u for u in users.User.query.all()}

    def get_answers_from_question(i):
        answers = [
            {
                'student': users_dict[answer_object.user_id],
                'answer':  answer_object.answers['questions'][i]['answer']
            }
            for answer_object in answers_objects
        ]

        res = defaultdict(list)
        for answer in answers:
            res[answer['answer']].append(answer['student'].name)

        try:
            res.pop(None)
        except KeyError:
            pass

        return [
            {'students': students, 'answer': answer}
            for answer, students in res.items()
        ]

    return flask.jsonify([
        {
            'title': question.title,
            'gradesByAnswer': question.grade_by_answer,
            'coefficient': question.coefficient,
            'answers': get_answers_from_question(i),
        }
        for i, question in enumerate(questions)
    ])


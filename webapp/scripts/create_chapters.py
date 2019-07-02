from app import db, app
from datetime import date
from sqlalchemy.exc import IntegrityError
from lessons import Chapter


CHAPTERS = [
    {
        'id': '01-HTML-CSS',
        'name' : 'HTML et CSS',
        'end_date': date(2019, 9, 12),
        'questions': [
            {
                'title':
                    "In the following piece of code, list all"
                    " the attributes of the <code>p</code> tag (separate"
                    " the attributes with a space; I'm not asking about"
                    " the values, give only the attributes!)? <br />"
                    " <code><pre>"
                    "  &lt;p id='head' class='column-3' data-userid='42'>"
                    "    Hello world!"
                    "  &lt;/p>",
                'grade_by_answer':{},
                'coefficient': 0.5,
            },
            {
                'title':
                    "Give three tags that belong to the head section"
                    " of an HTML page (i.e. between &lt;head> and &lt;/head>)."
                    " Separate your answers by a space" ,
                'grade_by_answer': {},
                'coefficient': 0.5,
            },
            {
                'title':
                    "Write a piece of HTML which displays \"Go to hell\""
                    " and is a link to the website \"http://666.com\".",
                'grade_by_answer': {},
                'coefficient': 0.5,
            },
        ],
    },
    {
        'id': '02-Elm',
        'name' : 'Elm',
        'end_date': date(2019, 9, 19),
        'questions': [],
    },
]

with app.app_context():
    db.create_all()
    for chapter in CHAPTERS:
        try:
            db.session.add(Chapter(**chapter))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("Chapter %s already exists" % chapter['id'])

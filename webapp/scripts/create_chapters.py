import sys

sys.path.append('.')

from app import  db, app
from datetime import date
from sqlalchemy.exc import IntegrityError
from blueprints.lessons import Chapter


CHAPTERS = [
    {
        'id': '01-HTML-CSS',
        'name' : 'HTML et CSS',
        'end_date': date(2019, 9, 15),
        'questions': [
            {
                'title':
                    "In the following piece of code, list all"
                    " the attributes of the <code>p</code> tag (separate"
                    " the attributes with a space; I'm not asking about"
                    " the values, give only the attributes!)? <br />"
                    " <code><pre>"
                    "&lt;p id='hello' class='column-3' data-userid='42'>"
                    "Hello world!"
                    "&lt;/p>",
                'coefficient': 0.5,
            },
            {
                'title':
                    "Give three tags that belong to the head section"
                    " of an HTML page (i.e. between &lt;head> and &lt;/head>)."
                    " Separate your answers with a space." ,

                'coefficient': 0.5,
            },
            {
                'title':
                    "Which one of the following is a <strong>valid</strong>"
                    " piece of HTML (enter 1, 2, 3 or 4):<ol>"
                    "<li><code>&lt;p>Lorem ipsum &lt;em>dolor &lt;strong>sit&lt;/strong>&lt;/em> amet&lt;/p></code></li>"
                    "<li><code>&lt;p>Lorem ipsum &lt;html>dolor &lt;strong>sit&lt;/strong>&lt;/html> amet&lt;/p></code></li>"
                    "<li><code>&lt;p>Lorem ipsum &lt;em>dolor &lt;strong>sit&lt;/em>&lt;/strong> amet&lt;/p></code></li>"
                    "<li><code>&lt;p>Lorem ipsum &lt;em>dolor &lt;strong>sit&lt;/strong>&lt;em> amet&lt;/p></code></li>"
                    "</ol>",

                'coefficient': 0.5,
            },
            {
                'title':
                    "Write a piece of HTML which displays \"Go to hell\""
                    " such as the text is a link to the website"
                    " \"http://666.com\".",

                'coefficient': 0.5,
            },
        ],
    },
    {
        'id': '02-Elm',
        'name' : 'Elm',
        'end_date': date(2019, 9, 19),
        'questions': [
            {
                'title':
                    "Let <code>f : String -> Int</code>"
                    " and <code>g : List Float -> Int</code>"
                    " be two functions. What is the type of"
                    " <code>h</code> where:"
                    " <pre>"
                    "   <code>h a b = f a + g b</code>"
                    " </pre>",
                'coefficient': 1,
            },
            {
                'title':
                    "How to produce the following piece of HTML in Elm?"
                    "<pre>"
                    "  <code>"
                    "&lt;ul>&lt;li>Hi Marvin!&lt;/li>&lt;/ul>"
                    "  </code>"
                    "</pre>",
                'coefficient': 1,
            },
            {
                'title':
                    'Write a function <code>f</code> (<em>without</em> '
                    ' the type annotation) which converts a'
                    ' list of integers into a list of string. For instance'
                    ' <code>f [2, 3, 5, 7] == ["2", "3", "5", "7"]</code>.'
                    ' All the functions you need are in the slides.',
                'coefficient': 1,
            },
            {
                'title':
                    '<code>ageStr</code> is a string entered by a user.'
                    ' Define a variable <code>ageInt</code> which is'
                    ' the conversion of <code>ageStr</code> in <code>Int</code'
                    ' if it is a correct representation of an <code>Int</code>'
                    ' or <code>-1</code> otherwise.',
                'coefficient': 1,
            },

        ],
    },
    {
        'id': '03-HTTP',
        'name': 'HTTP',
        'end_date': date(2019, 9, 26),
        'questions': [],
    }
]

with app.app_context():
    db.create_all()
    for chapter in CHAPTERS:
        for question in chapter['questions']:
            question['grades_by_answer'] = {}
        try:
            db.session.merge(Chapter(**chapter))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("Chapter %s already exists" % chapter['id'])

import sys, os

sys.path.append('.')

from app import app
from database import db
from datetime import date
from sqlalchemy.exc import IntegrityError
from blueprints.lessons import Chapter
from blueprints.chapter_http import AnswerForHttp
import json

import sqlalchemy
import blueprints.answers as answers


CHAPTERS = [
    {
        'id': '01-HTML-CSS',
        'name' : 'HTML et CSS',
        'end_date': date(2019, 9, 15),
        'questions': [
            {
                'title':
                    "In the following piece of code, list all"
                    " the attributes of the <code>p</code> tag,"
                    " one per line (I'm not"
                    " asking about"
                    " the values, give only the attributes!)? <br />"
                    " <code><pre>"
                    "&lt;p id='hello' class='column-3' data-userid='42'>"
                    "Hello world!"
                    "&lt;/p>"
                    "</pre></code>",
                'coefficient': 0.5,
            },
            {
                'title':
                    "Give three tags that belong to the head section"
                    " of an HTML page, one per line"
                    " (i.e. between &lt;head> and &lt;/head>).",

                'coefficient': 0.5,
            },
            {
                'title':
                    "Describe in a few words the role of HTML and CSS.",
                'coefficient': 1,
            },
            {
                'title':
                    "HTML is an acronym. What is its expanded form?",
                'coefficient': 0.25,
            },
            {
                'title':
                    "What is the role of <code>&amp;nbsp;</code>"
                    " in an HTML file?",
                'coefficient': 0.5,
            },
            {
                'title':
                    "What do we have to write in HTML to render the"
                    " <code>&lt;</code> symbol?",
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
                    "Write a piece of HTML that displays \"Go to hell\""
                    " such as the text is a link to the website"
                    " \"http://666.com\".",

                'coefficient': 0.5,
            },
            {
                'title':
                    'I am browsing a website at "http://example.org/blog/". What'
                    ' will be the address of my browser if I click on:'
                    ' <code><pre>&lt;a href="/userlist/"></pre></code>',
                'coefficient': 0.25,
            },
            {
                'title':
                    'Warning, this is not the same question! I am browsing a website at "http://example.org/blog/". What'
                    ' will be the address of my browser if I click on:'
                    ' <code><pre>&lt;a href="userlist/"></pre></code>',
                'coefficient': 0.25,
            },
            {
                'title':
                    'Be careful! I am browsing a website at "http://example.org/blog". What'
                    ' will be the address of my browser if I click on:'
                    ' <code><pre>&lt;a href="userlist/"></pre></code>',
                'coefficient': 0.25,
            },
            {
                'title':
                    'This is the last question about urls! '
                    ' I am browsing a website at "http://example.org/blog". What'
                    ' will be the address of my browser if I click on:'
                    ' <code><pre>&lt;a href="userlist/"></pre></code>',
                'coefficient': 0.25,
            },
            {
                'title':
                    'Give a CSS selector for the <code>p</code> tags'
                    ' inside a node with class <code>major</code>.',
                'coefficient':1,
            },

        ],
    },
    {
        'id': '02-Elm',
        'name' : 'Elm',
        'end_date': date(2019, 9, 19),
        'questions': [
            {   'title':
                    "Write a <code>mult</code> function"
                    " w(ith type annotation) taking two arguments and"
                    " multiplying them.",
                'coefficient': 0.5,
            },
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
                    'Write a function <code>f</code> (with'
                    ' type annotation) that converts a'
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
    },
    {
        'id': '04-AJAX',
        'name': 'Json and Elm decoders',
        'end_date': date(2019, 10, 2),
        'questions': [
            {
                'title':
                    'In Elm, what type do we use if we want represent'
                    ' failure with an error message?',
                'coefficient': 0.5,
            },
            {
                'title':
                    'True or false? In a <code>Result</code>,'
                    ' the error and the value types'
                    ' can be the same.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'Write a piece of JSON respresenting multiple'
                    ' animals: Bud, a dog; Kit, a cat and Bob, a fish',
                'coefficient': 1,
            },
            {
                'title':
                    'JSON is an acronym. What is its expanded form?',
                'coefficient': 0.5,
            },
            {
                'title':
                    'True or false? Json can only be use with Javascript.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'True or false? A JSON object can'
                    ' <strong>only</strong> be decoded'
                    ' to an Elm record containing the same number'
                    ' of fields.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'True or false? A field in a JSON object can'
                    ' <strong>only</strong> be decoded'
                    ' to an Elm field record with the same name.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'Write out a type and a decoder for the following'
                    ' piece of JSON:'
                    ' <code><pre>{\n'
                    '   "stars": 5,\n'
                    '   "followers": [ "Ford", "Arthur"],\n'
                    '   "name": "Marvin"\n'
                    '}</pre></code>',
                'coefficient': 1.5,
            }

        ],
    },
    {
        'id': '05-security',
        'name': 'User account and security',
        'end_date': date(2019, 10, 9),
        'questions': [
            {
                'title':
                    'How should you store the passwords of the users in the'
                    ' database?',
                'coefficient': 0.5,
            },
            {
                'title':
                    'What mechnanism or technology does permit to'
                    ' <strong>safely</strong> send the password user to the server?',
                'coefficient': 0.5,
            },
            {
                'title':
                    'True or false? When dealing with password hashes, it is safe'
                    ' to take the same salt for all the passwords.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'Give a simple solution to mitigate the effects of a session'
                    ' hijacking.',
                'coefficient': 0.5,
            },
            {
                'title':
                    'How are the cookies shared between the client and the'
                    ' server?',
                'coefficient': 1,
            },
            {
                'title':
                    'True or False? A malicious user can be logged in to an account'
                    ' on a website without providing the password of this account.'
                    ' If true, explain how, otherwise explain  why (give only the'
                    '"big idea").',
                'coefficient': 1,
            },
            {
                'title':
                    'In the following piece of code, <code>form</code> is a'
                    ' dictionary containing the input from the user.'
                    ' You can see here a request performed in an instant messaging'
                    ' software. This reuqest searches the messeages sent to a given'
                    ' user among all the messages from the current user.'
                    ' <pre><code>cur.execute("SELECT * FROM messages WHERE'
                    ' to_userd_id=\'" + form["to_user_id"] + "\' AND'
                    ' author_id=" + current_user.get_id())</code></pre>'
                    ' What value could a malicious user use for the "to_user"'
                    ' field in order to get all the messages in the database?',
                'coefficient': 1.5,
            },
            {
                'title':
                    'Rewrite this following piece of code to prevent SQL'
                    ' injections:'
                    ' <pre><code>cur.execute("SELECT * FROM messages WHERE'
                    ' to_userd_id=\'" + form["to_user_id"] + "\' AND'
                    ' author_id=" + current_user.get_id())</code><pre>',
                'coefficient': 0.5,
            },

        ],
    },
]


with app.app_context():
    db.create_all()
    for chapter in CHAPTERS:
        for question in chapter['questions']:
            question['grade_by_answer'] = {}
        chapter['questions'] = json.dumps(chapter['questions'])

        db.session.merge(Chapter(**chapter))
        db.session.commit()

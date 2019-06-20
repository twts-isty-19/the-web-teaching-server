from app import db, Chapter
from datetime import date
from sqlalchemy.exc import IntegrityError


db.create_all()

CHAPTERS = [
    {
        'id': '01-HTML-CSS',
        'name' : 'HTML et CSS',
        'end_date': date(2019, 9, 12),
    },
    {
        'id': '02-JS',
        'name' : 'Javascript',
        'end_date': date(2019, 9, 19),
    },
]

for chapter in CHAPTERS:
    try:
        db.session.add(Chapter(**chapter))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Chapter %s already exists" % chapter['id'])


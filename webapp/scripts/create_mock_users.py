import sys

sys.path.append('.')

from app import db, app
from datetime import date
from sqlalchemy.exc import IntegrityError
from blueprints.users import User


password = "12345"
email = "test@example.fr"

users = [
    ("stud@dom.org", "Student", False),
    ("teach@dom.org", "Teacher", True)
]

users_inserted = []
with app.app_context():
    db.create_all()
    for (email, name, is_teacher) in users:
        user = User(
            email=email,
            name=name,
            is_teacher=is_teacher,
        )
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            users_inserted.append((email, name, is_teacher))
        except IntegrityError:
            db.session.rollback()


print("Users inserted in the DB with password %s:" % (password))
for (email, name, is_teacher) in users_inserted:
    print(email, name, ": Teacher" if is_teacher else ": Student")


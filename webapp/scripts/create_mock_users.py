import sys

sys.path.append('.')

from app import db, app
from datetime import date
from sqlalchemy.exc import IntegrityError
from blueprints.users import User


password = "12345"
email = "test@example.fr"

u1 = User(
    email=email,
    name="Toto",
)
u1.set_password(password)

with app.app_context():
    db.create_all()
    db.session.add(u1)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

print("User %s with password %s is in the DB" % (email, password))

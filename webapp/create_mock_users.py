from app import db, app
from datetime import date
from sqlalchemy.exc import IntegrityError
from users import User


password = "12345"

u1 = User(
    email="test@example.fr",
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

print("User %s with password %s is in the DB" % (u1.email, password))

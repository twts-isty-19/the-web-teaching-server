from app import db, User
from datetime import date
from sqlalchemy.exc import IntegrityError


db.create_all()

u1 = User(
    email="test@example.fr",
    name="Toto",
)
u1.set_password("12345")

db.session.add(u1)
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    print("User %s already created." % u1.email)

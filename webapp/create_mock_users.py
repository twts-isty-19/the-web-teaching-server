from app import db, User
from datetime import date
from sqlalchemy.exc import IntegrityError


db.create_all()

password = "12345"

u1 = User(
    email="test@example.fr",
    name="Toto",
)
u1.set_password(password)

db.session.add(u1)
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()

print("User %s with password %s is in the DB" % (u1.email, password))

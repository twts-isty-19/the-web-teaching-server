import app
import users

USERS = [
    ("Sébastien", "sebsheep@yahoo.fr"),
]




with app.app.app_context():
    app.db.create_all()
    users.create_users(USERS, app.mail)

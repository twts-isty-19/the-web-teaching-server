import sys

sys.path.append('.')

import app
import blueprints.users as users

USERS = [
    ("Student Test", "stud@dom.org"),
]




with app.app.app_context():
    app.db.create_all()
    users.create_users(USERS, app.mail)

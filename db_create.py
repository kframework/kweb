from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db, models
import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

user_passwords = raw_input('User default password? : ').strip()
default_user = models.User(role = models.ROLE_ADMIN, email = 'default')
default_user.set_password(user_passwords)
available_user = models.User(role = models.ROLE_USER, email = 'available')
available_user.set_password(user_passwords)

print 'You may now log in as user default!'

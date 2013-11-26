from app import db
from config import *
import hashlib, shutil

# Constants for user roles
ROLE_USER = 0
ROLE_ADMIN = 1

# Join table to allow many-to-many relationship 
# between users and collections in SQLAlchemy
subscribers = db.Table('subscribers',
    db.Column('collection_id', db.Integer, db.ForeignKey('collection.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

# User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120))
    collections = db.relationship('Collection', secondary = subscribers, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    role = db.Column(db.SmallInteger, default = ROLE_USER)

    # Set password and commit
    def set_password(self, password):
        h = hashlib.sha224(SALT)
        h.update(password)
        self.password = h.hexdigest()
        db.session.add(self)
        db.session.commit()

    def is_password(self, password):
        h = hashlib.sha224(SALT)
        h.update(password)
        return self.password == h.hexdigest()

    def __repr__(self):
        return '<User %r>' % (self.email)

    # ----- Generic flask-login methods

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    # ----- End generic methods

    def is_admin(self):
        return self.role == ROLE_ADMIN

    # Check if user is subscribed to collection with id collection_id
    def is_subscribed(self, collection_id):
        return self.collections.filter(subscribers.c.collection_id == collection_id).count() > 0

    # Subscribe user to collection collection_id
    def subscribe(self, collection_id):
        if not self.is_subscribed(collection_id):
            collection = Collection.query.filter_by(id=collection_id).first()
            if collection is not None:
                self.collections.append(collection)
                db.session.add(self)
                db.session.commit()
                collection.copy_self(self)

    # Unsubscribe user from collection collection_id
    def unsubscribe(self, collection_id):
        if self.is_subscribed(collection_id):
            collection = Collection.query.filter_by(id=collection_id).first()
            if collection is not None:
                self.collections.remove(collection)
                if collection.owner_email == self.email:
                    collection.destroy()
                db.session.add(self)
                db.session.commit()

# Collection model
class Collection(db.Model):
    __tablename__ = 'collection'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(120))
    owner_email = db.Column(db.String(120), db.ForeignKey('user.email'), default='default')
    tool = db.Column(db.String(120), default = DEFAULT_TOOL)
    description = db.Column(db.String(160))

    def __repr__(self):
        return '<Collection %r>' % (self.name)

    # Returns: full path for collections files including trailing '/'
    def get_collection_path(self):
        return BASE_DIR + str(self.owner_email) + '/' + self.name + '/'

    # File operations: include file name on top of base path as String
    def add(file):
        open(self.get_collection_path())

    # Copy collection into workspace owned by new_owner
    def copy_self(self, new_owner):
        new_collection = Collection(name=self.name, owner_email=new_owner.email, tool=self.tool, description=self.description)
        if '..' in str(new_collection.get_collection_path()) or '~' in str(new_collection.get_collection_path()):
            # Throw exception and die.
            'i' + 1
        try:
            shutil.rmtree(new_collection.get_collection_path())
        except:
            pass
        shutil.copytree(self.get_collection_path(), new_collection.get_collection_path())
        new_owner.collections.remove(self)
        new_owner.collections.append(new_collection)
        db.session.add(new_owner)
        db.session.add(new_collection)
        db.session.commit()
        return new_collection

    def destroy(self):
        try:
            shutil.rmtree(self.get_collection_path())
        except:
            pass
        db.session.delete(self)
        db.session.commit()

# Pseudo-model for anonymous collections
# Used polymorphically with the "Collection"
# model, using the tools in collection_tools.py
# and does not get stored to the database, but rather
# is stored client-side by the user's session as a
# Picked object
class AnonymousCollection:
    def __init__(self, id):
        self.uuid = id
        self.owner_email = 'anon'

    def copy_from_collection(self, collection):
        self.name = collection.name
        self.tool = collection.tool
        self.id = collection.id
        self.description = collection.description
        shutil.copytree(collection.get_collection_path(), self.get_collection_path())

    def get_collection_path(self):
        return BASE_DIR + 'anon/' + str(self.uuid) + '/' + self.name + '/'

    def destroy(self):
        try:
            shutil.rmtree(self.get_collection_path())
        except:
            pass

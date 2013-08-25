# Utilities for collection control (accessed by views.py)

from models import User, Collection, AnonymousCollection
from flask import g, session, request
from config import BASE_DIR
import uuid

def get_user_collections(email):
    if email is None:
        return Collection.query.all()
    user = User.query.filter_by(email = email).first()
    return user.collections

# Get connection for current session, request
def get_current_collections():
    # Choose between anonymous collection object and loggede in collection
    if not g.user.is_anonymous():
        return get_user_collections(g.user.email)
    if session.get('collections'):
        return session.get('collections')
    # Base case: Anonymous user with no previous visits
    new_uuid = uuid.uuid4()
    # Create and return a copy of default's collections as AnonymousCollection
    new_collections = []
    for collection in get_user_collections('default'):
        new_collection = AnonymousCollection(new_uuid)
        new_collection.copy_from_collection(collection)
        new_collections.append(new_collection)
    session['collections'] = new_collections
    return new_collections

# Return the number of collections in list of collections
def count_collections(collections):
    if g.user.is_anonymous():
        return len(collections)
    return collections.count()

# Get collection from collection ID
# (whether user is logged in or not)
def get_collection(id):
    if g.user.is_anonymous():
        for collection in session['collections']:
            if collection.id == id:
                return collection
        return None
    return Collection.query.filter_by(id=id).first()

# Get metadata or a file
def get_file_meta():
    try:
        file = request.args.get('file', None, type = str)
        path = request.args.get('path', None, type = str)
        collection_id = request.args.get('collection_id', None, type = int)
        collection = get_collection(collection_id)
        file_path = file + path
        if '..' in file_path or '~' in file_path:
            return ''
        return open(collection.get_collection_path() + path + file + '.meta').read()
    except:
        pass
    try:
        return open(collection.get_collection_path() + path + '.meta').read()
    except:
        return ''

# Get path for current request assuming standard GET request with file, path, collection_id args
def get_file_path():  
    file = request.args.get('file', None, type = str)
    path = request.args.get('path', None, type = str)
    collection_id = request.args.get('collection_id', None, type = int)
    collection = get_collection(collection_id)
    file_path = collection.get_collection_path() + str(path) + str(file)
    # For security reject .. or ~ paths
    if '..' in file_path or '~' in file_path:
        return ''
    return file_path

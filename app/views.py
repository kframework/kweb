from flask import render_template, flash, redirect, jsonify, request, url_for, g, flash, session, send_from_directory, make_response
from app import app, lm, db
from forms import *
from commands import Command
from models import *
from config import *
from flask.ext.login import login_user, logout_user, current_user, login_required
from collection_tools import *
import hashlib, uuid, time, shutil, os
from werkzeug import secure_filename
from ansi2html import Ansi2HTMLConverter

# Home Page
@app.route('/')
def hello_world():
    return render_template('index.html', title = 'Home')

# Login Page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect('..')
    # Create the login and registration forms
    # Prefixes are to distinguish them on-page
    registerform = RegistrationForm(request.form, prefix='register')
    loginform = LoginForm(request.form, prefix='login')
    if request.method == 'POST':
        if loginform.email.data and loginform.validate():
            # Success, do login!
            return do_login(loginform, registerform)
        if registerform.email.data and registerform.validate():
            # Success, do register!
            return do_register(registerform)
        flash('Login/Register failed.  Please try again.', category='error')
        return render_template('login.html', loginform = loginform, registerform = registerform, title = 'Login/Register')
    return render_template('login.html', loginform = loginform, registerform = registerform, title = 'Login/Register')

# Forgot password page
# Unfinished: @todo finish this
@app.route('/forgot', methods = ['GET', 'POST'])
def forgot():
    if g.user is not None and g.user.is_authenticated():
        return redirect('..')
    forgotform = ForgotForm(request.form)
    if request.method == 'POST':
        if forgotform.validate():
            # Success, e-mail a new password
            return do_forgot(forgotform)
        return render_template('forgot.html', forgotform = forgotform, title='Forgot Password', failed=True, sent=False)
    return render_template('forgot.html', forgotform = forgotform, title='Forgot Password', failed=False, sent=False)

# Tool Execution Page
# Allow for tool change via /run/[toolname]
@app.route('/run/', defaults={'tool': DEFAULT_TOOL})
@app.route('/run/<string:tool>')
def base_run(tool):
    return render_template('run.html', title = 'Run ' + tool.upper() + ' Online', tool=tool, collections=get_current_collections(), open_path = request.args.get('open_path', 'tutorial/', type = str), hidden = request.args.get('hidden', 0, type=int), autoload = request.args.get('autoload', '', type=str))

# Embedded tool execution page with no header.
@app.route('/run_embed/', defaults={'tool': DEFAULT_TOOL})
@app.route('/run_embed/<string:tool>')
def embed_run(tool):
    response = make_response(render_template('run_embed.html', title = 'Run ' + tool.upper() + ' Online', tool=tool, collections=get_current_collections(), open_path = request.args.get('open_path', '', type = str), hidden = request.args.get('hidden', 0, type=int), autoload = request.args.get('autoload', '', type=str)))
    # This is a hack to get around issues embedding pages with cookies in IE
    response.headers['P3P'] = 'CP="No compact P3P policy available!"'
    return response

# Logout Page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer)

# Admin page - manage users
@app.route('/manage_users')
@login_required
def manage_users():
    if not g.user.role:
        return redirect('..')
    return render_template('manage_users.html', title = 'Manage Users', all_users = User.query.all())

# Admin page - manage collections
@app.route('/manage_collections', methods=['GET', 'POST'])
@login_required
def manage_collections():
    if not g.user.role:
        return redirect('..')
    newform = NewCollectionForm(request.form, prefix='new')
    editform = EditCollectionForm(request.form, prefix='edit')
    if request.method == 'POST':
        if newform.name.data and newform.validate():
            user = User.query.filter_by(email = newform.owner.data).first()
            if user is not None:
                collection = Collection(tool = newform.tool.data, name = newform.name.data, owner_email=newform.owner.data, description=newform.description.data)
                user.collections.append(collection)
                db.session.add(collection)
                db.session.commit()
                flash('Collection ' + newform.name.data + ' added.', category='success')
            else:
                flash('Error: No such user', category='error')
        if editform.id.data and editform.validate():
            collection = Collection.query.filter_by(id=int(editform.id.data)).first()
            if collection is not None:
                if editform.name.data:
                    collection.name = editform.name.data
                if editform.tool.data:
                    collection.tool = editform.tool.data
                if editform.description.data:
                    collection.description = editform.description.data
                db.session.add(collection)
                db.session.commit()
                flash('Collection updated successfully', category='success')
            else:
                flash('Error: Invalid collection ID', category='error')
    return render_template('manage_collections.html', title = 'Manage Collections', newform = newform, editform=editform, all_collections = get_user_collections(None))

# User settings page - manage user collections
@app.route('/settings', methods = ['GET', 'POST'])
@login_required
def settings():
    settingsform = SettingsForm(request.form, prefix='settings')
    if request.method == 'POST' and settingsform.data and settingsform.validate():
        if settingsform.password.data:
            g.user.set_password(settingsform.password.data)
            flash('Successfully changed password.', category='success')
        if settingsform.email.data:
            g.user.email = settingsform.email.data
            db.session.add(g.user)
            db.session.commit()
            flash('Successfully changed email.', category='success')
    return render_template('settings.html', title='User Settings', settingsform=settingsform, default_collections = get_user_collections('default'), available_collections=get_user_collections('available'))

# All views defined below are not user-facing

# Internal Page (tool execution worker)
@app.route('/_run_code')
def run_code():
    code = request.args.get('code', None, type = str)
    action = request.args.get('action', None, type = str)
    path = request.args.get('path', None, type = str)
    current_file = request.args.get('file', None, type = str)
    collection_id = request.args.get('collection_id', None, type = int)
    args = request.args.get('args', '', type = str)
    collection = get_collection(collection_id)
    if collection:
        current_path = collection.get_collection_path() + path
    else:
        current_path = None
        current_file = None
        args = ''
        code = None
    return jsonify(result = parse_code(code, 'k', action, current_path, current_file, args))

# Internal Page (result div update worker)
@app.route('/_update_result/<string:curr_id>')
def update_result(curr_id):
    try:
        base_path = BASE_DIR + 'results/' + curr_id
        conv = Ansi2HTMLConverter()
        return jsonify(result = conv.convert(open(base_path).read().strip()), done=os.path.exists(base_path+'.done'))
    except:
        return jsonify(result = 'No jobs pending.', done=False)

@app.route('/_file_browser/<string:tool>')
def file_browser(tool):
    return render_template('file_browser.html', tool=tool, collections=get_current_collections(), open_path = request.args.get('open_path', None, type = str), hidden = request.args.get('hidden', 0, type=int))

@app.route('/_update_stdin/<string:curr_id>')
def update_stdin(curr_id):
    stdin = request.args.get('stdin', None, type=str)
    if not stdin:
        return jsonify(success=False, error='No stdin provided.')
    try:
        base_path = BASE_DIR + 'results/' + curr_id
        if (os.path.exists(base_path + '.done')):
            return jsonify(success=False, error='No process currently running.')
        fd = int(open(base_path + '.in').read())
        print 'FD: ' + str(fd)
        os.write(fd, stdin + '\n')
        open(base_path, 'a').write(stdin + '\n')
        return jsonify(success=True)
    except:
        return jsonify(success=False, error='An error occured in sending your stdin.')

# Internal Page (file restore worker)
@app.route('/_restore_file')
def restore_file():
    path = request.args.get('path', None, type = str)
    file = request.args.get('file', None, type = str)
    tool = request.args.get('tool', None, type = str)
    if '..' in path or '..' in file or '~' in file or '~' in path:
        return redirect('..')
    collection_id = request.args.get('collection_id', None, type=int)
    collection = get_collection(collection_id)
    original_collection = Collection.query.filter_by(owner_email = 'default', tool = tool, name = collection.name).first()
    if not original_collection:
        original_collection = Collection.query.filter_by(owner_email = 'available', tool = tool, name = collection.name).first()
    if not original_collection:
        return jsonify(success=False)
    add_on_path = str(path) + str(file)
    try:
        original_path = os.path.join(original_collection.get_collection_path(), add_on_path)
        new_path = os.path.join(collection.get_collection_path(), add_on_path)
        if os.path.isdir(original_path):
            shutil.rmtree(new_path)
            shutil.copytree(original_path, new_path)
        else:
            shutil.copy(original_path, new_path)
        return jsonify(success=True)
    except:
        return jsonify(success=False)

# Internal Page (file save worker)
@app.route('/_save_file')
def save_file():
    code = request.args.get('code', None, type = str)
    path = request.args.get('path', None, type = str)
    file = request.args.get('file', None, type = str)
    if '..' in path or '..' in file or '~' in file or '~' in path:
        return redirect('..')
    collection_id = request.args.get('collection_id', None, type=int)
    collection = get_collection(collection_id)
    reload = ''
    if not g.user.is_anonymous() and collection.owner_email != g.user.email:
        collection = collection.copy_self(g.user)
        reload = 'Reload required.'
    file_path = collection.get_collection_path() + path + file
    print 'Saving ' + file_path + ' in ' + str(collection_id)
    try:
        file = open(file_path, 'w')
        file.write(code)
        file.close()
        return jsonify(result='Save successful. ' + reload)
    except:
        return jsonify(result='Error: saving failed.  Please try reloading again, and if this does not work e-mail the webmaster (phil@linux.com) with information about what you were trying to save.')

# Internal Page (collection unsubscribe)
@app.route('/_unsubscribe/<int:id>')
@login_required
def unsubscribe(id):
    flash('Unsubscribed from collection successfully.', category='success')
    g.user.unsubscribe(id)
    return redirect(request.referrer)

# Internal Page (collection subscribe)
@app.route('/_subscribe/<int:id>')
@login_required
def subscribe(id):
    flash('Subscribed to collection successfully.', category='success')
    g.user.subscribe(id)
    return redirect(request.referrer)

# Internal Page (collection delete)
@app.route('/_delete_collection/<int:id>')
@login_required
def delete_collection(id):
    if not g.user.role:
        return redirect('..')
    collection = Collection.query.filter_by(id=id).first()
    if collection is not None:
        collection.destroy()
        flash('Collection deleted successfully', category='success')
    else:
        flash('Error: Collection does not exist', category='error')
    return redirect(url_for('manage_collections'))

# Internal Page (user delete)
@app.route('/_delete_user/<int:id>')
@login_required
def delete_user(id):
    if not g.user.role:
        return redirect('..')
    user = User.query.filter_by(id=id).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', category='success')
    else:
        flash('Error: User does not exist', category='error')
    return redirect(url_for('manage_users'))

# Internal Page (user promote/demote)
@app.route('/_change_user_role/<int:id>')
@login_required
def change_user_role(id):
    if not g.user.role:
        return redirect('..')
    user = User.query.filter_by(id=id).first()
    if user is not None:
        # Toggle user role
        user.role = 0 if user.role == 1 else 1
        db.session.add(user)
        db.session.commit() 
        flash('User role changed successfully', category='success')
    else:
        flash('No such user.', category='error')
    return redirect(url_for('manage_users'))

# Internal Page (administrative login as user)
@app.route('/_login_as_user/<int:id>')
@login_required
def login_as_user(id):
    if not g.user.role:
        return redirect('..')
    user = User.query.filter_by(id=id).first()
    logout_user()
    login_user(user)
    flash('Successfully logged in as ' + user.email, category='success')
    return redirect(url_for('hello_world'))

# Internal Page (file loader)
@app.route('/_load_file')
def load_file():
    meta = get_file_meta()
    try:
        my_file = open(get_file_path())
        result = my_file.read()
        my_file.close()
        return jsonify(path=request.args.get('file', None, type=str), result=result, meta=meta)
    except:
        return jsonify(result='File not found or could not be loaded: ' + get_file_path(), path='Try another example.', meta = '')

# Internal Page (file downloader)
@app.route('/_download_file')
def download_file():
    file_path = get_file_path().split('/')
    file_name = file_path[-1]
    file_directory = '/'.join(file_path[:-1])
    if os.path.isdir(os.path.join(file_directory, file_name)):
        zip_info = get_directory_zip(os.path.join(file_directory, file_name))
        return send_from_directory(zip_info[0], zip_info[1], as_attachment=True, attachment_filename = file_name + '.zip')
    return send_from_directory(file_directory, file_name, as_attachment=True)

# Internal Page (file deletion worker)
@app.route('/_delete_file')
def delete_file():
    try:
        os.remove(get_file_path())
    except:
        pass
    return jsonify(result=None)  

# Internal Page (directory deletion worker)
@app.route('/_delete_directory')
def delete_directory():
    try:
        shutil.rmtree(get_file_path())
    except:
        pass
    return jsonify(result=None)  

# Internal Page (file creation worker)
@app.route('/_create_file')
def create_file():
    try:
        file_name = request.args.get('file_name', None, type=str)
        file_path = get_file_path() + '/' + file_name
        if not '..' in file_path and not '~' in file_path:
            open(file_path, 'w').write('')
            return jsonify(result=None)
        return ''
    except:
        return ''

# Internal Page (directory creation worker)
@app.route('/_create_directory')
def create_directory():
    file_name = request.args.get('file_name', None, type=str)
    file_path = get_file_path() + '/' + file_name
    if not '..' in file_path and not '~' in file_path:
        if not os.path.isdir(file_path):
            os.makedirs(file_path)
        return jsonify(result=None)
    return ''

# Internal Page (Flask upload handler)
@app.route('/_upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    collection = request.form['collection']
    path = request.form['path']
    if '..' in path or '~' in path:
        return ''
    filename = secure_filename(file.filename)
    file.save(os.path.join(get_collection(int(collection)).get_collection_path() + path, filename))
    flash('Successfully uploaded ' + filename + ' in ' + path, category='success')
    return redirect(request.referrer)

# Internal Page (register handler)
def do_register(registerform):
    if User.query.filter_by(email=registerform.email.data).first() is not None:
        flash('Registration failed.  User already exists.', category='error')
        return redirect(url_for('login'))
    user = User(email=registerform.email.data, password='')
    user.collections.extend(User.query.filter_by(email='default').first().collections)
    user.set_password(registerform.password.data)
    login_user(user)
    flash('Welcome to FSLRun!  Please feel free to browse the help provided above.', category='success')
    return redirect(url_for('hello_world'))

# Internal Page (login handler)
def do_login(loginform, registerform):
    user = User.query.filter_by(email = loginform.email.data).first()
    if user and user.is_password(loginform.password.data):
        login_user(user)
        flash('You are now logged in.', category='success')
        return redirect(url_for('hello_world'))
    flash('Login failed.  Incorrect username or password', category='error')
    return redirect(url_for('login'))

# Internal Page (forgot password handler)
def do_forgot(forgotform):
    user = User.query.filter_by(email = forgotform.email.data).first()
    if user:
        try:
            # @todo Generate a new password for the user
            # E-mail generated password to user
            return render_template('forgot.html', forgotform = forgotform, title='Forgot Password', failed=False, sent=True)
        except:
            pass
    return render_template('forgot.html', forgotform = forgotform, title='Forgot Password', failed=True, sent=False)

# Convert the directory represented by the arguments
# path and collection to a nested array with file data
# for use in displaying the file browser.
# Arg open_path represents the path file browser should initially open to.
def get_file_tree(path, collection, open_path):
    files = []
    try:
        file_list = os.listdir(collection.get_collection_path() + path)
        file_list.sort()
        for file in file_list:
            file_class = ''
            if os.path.isdir(collection.get_collection_path() + path + file):
                if file[0] != '.':
                    checked = 0
                    if open_path and (((path + file) in open_path)):
                        checked = 1
                    if open_path and open_path in collection.get_collection_path() + path + file:
                        checked = 2
                    disabled = False
                    if (file.split('-')[-1] == 'kompiled'):
                        disabled = True
                        file_class = 'kompiled-dir'
                    files.append({'directory': True, 'base_path': path, 'name': file, 'checked': checked, 'files': get_file_tree(path + file + '/', collection, open_path), 'collection_id': collection.id, 'disabled': disabled, 'file_class': file_class})
            else:
                if not '.meta' in file:
                    file_class = 'file'
                    if '.k' in file:
                        file_class = 'file-k'
                    if '.pdf' in file:
                        file_class = 'file-pdf'
                    files.append({'directory': False, 'base_path': path, 'name': file, 'collection_id': collection.id, 'file_class': file_class })
        return files
    except:
        return files

# Process the user input
def parse_code(code, tool, action, path, current_file, args):
    curr_id = str(uuid.uuid4())
    command = Command(code, tool, action, path, current_file, curr_id, args)
    command.run()
    return curr_id

# Set up globals in each request context
@app.before_request
def before_request():
    g.user = current_user
    g.tools = TOOLS
    g.get_file_tree = get_file_tree
    g.count_collections = count_collections
    g.str = str
    g.len = len

# Required by flask-login, see "user_loader" doc.
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

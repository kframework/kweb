# Copy file to config.py before use.

import os

# WTForms Cross-Site Scripting Protection
CSRF_ENABLED = True
SECRET_KEY = 'kisthebest'
SALT = 'kisthebest'

# Application-specific settings
BASE_HTTP_URL = 'http://localhost:8080/'
MAIL_SENDER = 'no-reply@my.domain'
DEFAULT_TOOL = 'k'
# Include trailing paths
BASE_DIR = '/home/kuser/kfiles/'
APP_DIR = '/home/kuser/fslrun/'

# Dictionary of tools with array of actions
# An action is a dictionary with two values
# action: name of the action the tool can perform
# stdin: 1 allow standard input capture
TOOLS = {
    'k': {'actions': [
                        {'action': 'Kompile', 'stdin': 0},
                        {'action': 'KRun', 'stdin': 1}
                     ]
         }
}

# ---------------------------------------------------------------------
# DO NOT CHANGE BELOW THIS LINE UNLESS YOU ARE SURE, ESP. IN PRODUCTION. 
# Session lifetime in days
SESSION_LIFETIME = 5

# Paths to database and migration directory
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(APP_DIR, 'db_repository')

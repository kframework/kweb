kweb
====

Online extensible IDE for the K Framework and other formal verification projects.  http://fsl.cs.uiuc.edu/tool for a demo.

Setup
===

Setup is fairly simple.  First, ensure you have Python 2.7 installed.

Then, perform the following steps (Python is short for your Python interpreter).

$ python virtalenv.py flask

$ source flask/bin/activate

$ pip install flask==0.9 flask-login sqlalchemy==0.8.1 flask-sqlalchemy==0.16 sqlalchemy-migrate flask-wtf ansi2html diff_match_patch flask-compress

$ cp sample_config.py config.py

$ cd [directory for file storage]

$ mkdir default anon results

$ cd [app dir]


$ vi config.py // UPDATE THE FOLDER PATHS

$ python db_create.py

$ python run.py

Navigate to localhost:8080 and you're all set!

Project Goals
===
The goal of the kweb project is an extensible online IDE which can be used to edit, save, and test code on a remote server in-browser.
Currently, a demo of the tool running K is available at http://fsl.cs.uiuc.edu/tool/

Style Guidelines
===
These are loose guidelines, readability is the most important.

Python:
- Tabs for spaces, four lines per space
- Single quoted string when possible
- Underscored method names and variables rather than camel case.

JavaScript:
- Two lines per indent
- Function bodies must start on their own line
- Underscore rather than camel case for variable, method names

HTML:
- Four lines per indent
- Container tags' children should be indented one level

CSS:
- No guidelines, keep it readable.

Known issues and bugs
===
See the Github page at https://github.com/kframework/k

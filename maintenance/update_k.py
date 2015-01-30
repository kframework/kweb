# This file is intended to provide an automatic update feature for using the K Framework with kweb.
# Running this script in the background as an upstart job (its intended use case) will watch a specified directory.
# When the directory is modified (a new K release is pushed, from a CI script or other), the script will launch an upgrade
# task for kweb after 45 seconds of waiting (to ensure any changes to the directory are complete).
# This task will run at most once an hour (both of the above numbers are configurable) to ensure kweb 
# functionality is never interrupted for too long.
# -------------
# SCRIPT DEPENDENCIES: inotify-tools and Python requests

# Wait after directory change, in seconds
WAIT_AFTER_DIRECTORY_CHANGE = 45
# Time to wait to check for next upgrade after upgrade finishes
WAIT_AFTER_UPGRADE = 0
# Directory to watch for K upgrades (include trailing /)
DIRECTORY_TO_WATCH = '/srv/www/k/imgs/releases/k'
# Directory to copy upgrades to (should be the same as directory kweb runs from, include trailing /)
COPY_TO_DIRECTORY = '/k'
# Directory to use as temporary storage directory (include trailing /)
TMP_STORAGE_DIRECTORY = '/tmp/k'
# URL for kweb home (include trailing /)
KWEB_URL='http://kframework.org/tool/'

import requests, os, time, shutil

# Keep same session to avoid kweb workspace duplication
s = requests.Session()

def notifyfailure(error):
    # @todo have this email authors
    print 'NOTIFYING: ' + error

def test_kweb():
    s.get(KWEB_URL + 'run')
    # Test lambda kompile
    try:
        r = s.get(KWEB_URL + '_run_code?code=&tool=k&path=1_k%2F1_lambda%2Flesson_1%2F&action=Kompile&file=lambda.k&collection_id=1&args=lambda.k&stdin=&_=1422626919018').json()
    except: 
        notifyfailure('workspace setup')
        return False
    if not 'result' in r:
        notifyfailure('kompiling lambda (initialization)')
        return False
    result_lookup_id = r['result']
    while True:
        try:
            r = s.get(KWEB_URL + '_update_result/' + str(result_lookup_id)).json()
            if 'done' in r and r['done']:
                if 'no output' in r['result']:
                    # Tests pass
                    return True
                print "Unexpected output!"
                return False
            time.sleep(2)
        except:
            # Can only be due to network issues
            return False

while True:
    try:
        print 'Waiting for K update'
        os.system('inotifywait -e modify -q ' + DIRECTORY_TO_WATCH)
        print 'K update started'
        time.sleep(WAIT_AFTER_DIRECTORY_CHANGE)
        os.system("killall -9 /srv/kweb/kweb/flask/bin/python")
        print 'Attempting kweb upgrade...'
        if os.path.exists(TMP_STORAGE_DIRECTORY):
            shutil.rmtree(TMP_STORAGE_DIRECTORY)
        shutil.move(COPY_TO_DIRECTORY, TMP_STORAGE_DIRECTORY)
        if os.path.exists(COPY_TO_DIRECTORY):
            shutil.rmtree(COPY_TO_DIRECTORY)
        shutil.copytree(DIRECTORY_TO_WATCH, COPY_TO_DIRECTORY)
        os.system('killall -9 maude.linux64')
        os.system('chmod -R 777 ' + COPY_TO_DIRECTORY)
        print 'Testing kweb upgrade...'
        if test_kweb():
            print 'Update completed successfully!'
            time.sleep(WAIT_AFTER_UPGRADE)
        else:
            print 'Update failed due to incompatibility with kweb!  Attempting to restore!'
            shutil.rmtree(COPY_TO_DIRECTORY)
            shutil.move(TMP_STORAGE_DIRECTORY, COPY_TO_DIRECTORY)
            if test_kweb():
                print 'Restore successful!'
                time.sleep(WAIT_AFTER_UPGRADE)
            else:
                notifyfailure('Critical failure, unrecoverable upgrade.  kweb is in inconsistent and broken state!')
    except: # Yes I know this is bad.
        print 'Update failed!'
        if os.path.exists(TMP_STORAGE_DIRECTORY):
            print 'Restoring temporary storage backup'
            try:
                shutil.rmtree(COPY_TO_DIRECTORY)
                shutil.move(TMP_STORAGE_DIRECTORY, COPY_TO_DIRECTORY)
                print 'Success!'
            except:
                print 'Failed to restore!  Try restoring manually!'
        time.sleep(WAIT_AFTER_UPGRADE)
        notifyfailure('Unknown error!')

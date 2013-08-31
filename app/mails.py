from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from config import MAIL_SENDER, BASE_HTTP_URL

# Send HTML mail html to emails owner_emails with
# subject subject
def send_html_mail(html, subject, owner_emails):
	if not owner_emails or not len(owner_emails):
		return False
	message = MIMEText(html, 'html')
	message['From'] = MAIL_SENDER
	message['To'] = ', '.join(owner_emails)
	message['Subject'] = subject
	p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
	p.communicate(message.as_string())
	# For debug / log purposes
	print "Mail sent to " + str(owner_emails) + " regarding " + subject

def send_forgot_mail(password_hash, user_email):
	html = 'You are receiving this e-mail because you have requested a password reset from kweb.' \
	+ '<br><br>Please visit ' + BASE_HTTP_URL + 'reset_password/' \
	+ password_hash + '/' + user_email + ' to choose a new password.'
	print html
	send_html_mail(html, 'kweb Password Reset', [user_email])

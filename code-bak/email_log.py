import os
import smtplib, ssl
from common import get_recipients

# paths relative to this file
parent_dir = os.path.dirname(os.path.abspath(__file__))
grandpa_dir = os.path.dirname(parent_dir)
creds_path = os.path.join(grandpa_dir, 'email', 'creds.txt')
pm_emails_path = os.path.join(grandpa_dir, 'email', 'receivers_pm.txt')
admin_emails_path = os.path.join(grandpa_dir, 'email', 'receivers_admin.txt')
params_path  = os.path.join(grandpa_dir, 'config', 'params.txt')


# send log by email
def send_email(log, subj, receivers):

	# expects one line such as: username:password
	with open(creds_path, 'r') as f:
		creds = f.read()

	username, password = creds.strip().split(":")
	receiver_list = get_recipients(admin_emails_path)

	# https://stackabuse.com/how-to-send-emails-with-gmail-using-python/
	port = 465  # For SSL
	receiver_list.extend(receivers)

	body = log.copy()

	body.insert(0, "")
	body.insert(0, "Subject: xDiff -- Logging from Ur -- " + subj)
	body.insert(0, f"To: {receiver_list[0]}")
	#body.insert(0, "Cc: emel.ince@capstan.be")
	body.insert(0, "From: cApps Bot")

	# Create a secure SSL context
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.googlemail.com", port, context=context) as server:
		# TODO: Send email here
		try:
			server.login(username, password)
			msg = "\r\n".join(body)
			server.sendmail(username, receiver_list, msg)
		except:
			log = print_log("ERROR: Email not sent", log)
			print("ERROR: Email not sent", log)



def compose_log():
	log = []
	msg = """Bom dia, alegria!
Keep it going, Google!
	"""
	log.append(msg)
	return log



if __name__ == "__main__":
	
	subj = "Keeping it awake"
	receivers = ['terminolator@gmail.com']
	log = compose_log()
	send_email(log, subj, receivers)
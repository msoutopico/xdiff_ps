import glob
import os
import sys
import requests
import json
from yattag import Doc
import webbrowser
from datetime import datetime
import smtplib, ssl
import os.path
import yagmail
from email_log import send_email
from common import get_recipients
from common import denormalize_path
from common import get_config_params
# sys.exit()

# paths relative to this file
parent_dir = os.path.dirname(os.path.abspath(__file__))
grandpa_dir = os.path.dirname(parent_dir)
creds_path = os.path.join(grandpa_dir, 'email', 'creds.txt')
admin_emails_path = os.path.join(grandpa_dir, 'email', 'receivers_admin.txt')
pm_emails_path = os.path.join(grandpa_dir, 'email', 'receivers_pm.txt')
params_path  = os.path.join(grandpa_dir, 'config', 'params.txt')

# global variables
data = {
	'token': '202020', # key to be provided by the API documentation
	'app': 'xdiff',
	'rows': 'different' # or identical
}

headers = {
	#'Content-type': 'multipart/form-data', # 
	'Content-Type' : 'application/x-www-form-urlencoded',
	'User-Agent': 'PostmanRuntime/7.19.0',
	'Accept': '*/*',
	'Cache-Control': 'no-cache',
	'Postman-Token': 'c0bfa615-5eab-42d1-bf0d-f2252f334c96',
	'Host': 'capps.capstan.be',
	'Accept-Encoding': 'gzip, deflate',
	'Connection': 'keep-alive'
}
#	'Content-Length': '1780620',

def files(path):
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			yield file

# real paths will be taken from the watcher
#dir_orig = "../Lab/4_CODING_GUIDES/01_VERIF_from_country"
#dir_edit = "../Lab/4_CODING_GUIDES/04_VERIF_reviewed_delivered"

# update log and print the update
def print_log(msg, log):
	print(msg)
	log.append(msg)
	return log


# define functions in a module and import it
def check_files_exist(omt_dir):
	global log
	omt_file_arr = [f for f in glob.glob(omt_dir + "/*.omt")]
	if len(omt_file_arr) > 1:
		log.append("There are more than one OMT files in " + omt_dir)
		return bool(False)
	if len(omt_file_arr) == 0:
		log.append("No OMT packages found in " + omt_dir)
		return bool(False)
	else:
		return omt_file_arr[0]
		# log.append("I will send files " + omt_file_orig[0] + " and " + omt_file_edit[0] + " to xDiff")


# write report file (containing link to the report page)
def write_report(result, filename, path):
	f = open(path + "/" + filename,"w+")
	f.write(result)
	f.close()


# create HTML page to put in the report file
def build_html_report(url):
	# re-direct meta
	meta = {
		'http-equiv': 'refresh',
		'content': '0; ' + url
	}
	doc, tag, text = Doc().tagtext()
	with tag('html'):
		with tag('head'):
			doc.stag('meta', **meta)
			#tag('meta', http-equiv="refresh", content="2; url = https://www.tutorialspoint.com")
		with tag('body'):
			with tag('a', href=url):
				text('Click to open the diff report')
	result = doc.getvalue()
	return result
	#print(result)


# write log to text file
def write_log(log, path, moment):
	# print log
	with open(path + '/log.txt', mode='a+', encoding='utf-8') as myfile:
		myfile.write('\n------------------------\n' + moment + '\n' + '\n'.join(log))
		# write log in folder 4_CODING_GUIDES\_Tech


# send files to xdiff
def post_to_xdiff(path_pair):

	print("path_pair is " + str(path_pair))

	# compose log
	log = []
	subj = "New report"
	log4pm = []

	log = print_log(f"\n{'=' * 50}\nNEW REQUEST", log)
	log = print_log("* Path pair: " + str(path_pair), log)

	dir_orig = path_pair['orig']
	dir_edit = path_pair['edit']

	timestamp = str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	xdiff_rpt_fn = f"xdiff_report_{timestamp}.html"
	# get path to both files if they exist (<= ternary?? )
	#sys.exit()

	# check that the files exist, not only the folders
	if check_files_exist(dir_orig) and check_files_exist(dir_edit):

		log = print_log("* Paths ok (exist): ", log)
		log = print_log(f"{dir_orig}\n{dir_edit}", log)

		# get paths to the two omt files
		path_to_omtfile_orig = check_files_exist(dir_orig)
		path_to_omtfile_edit = check_files_exist(dir_edit)

		# create dictionary with the two files to be posted
		files = {
			'omt_pkg_1': open(path_to_omtfile_orig, 'rb'),
			'omt_pkg_2': open(path_to_omtfile_edit, 'rb')
		}
		log = print_log("* Files:" + str(files), log)
		#sys.exit()

		# send request and get response
		log = print_log("* Request sent to xDiff", log)

		#diff_api_url = 'https://httpbin.org/post'
		params = get_config_params(params_path)
		diff_api_url = params['xdiff_url']
		r = requests.post(diff_api_url, files=files, data=data, headers=headers) #, allow_redirects=True
		# parse response
		
		print("Response starts")
		print(type(r))
		print(r)
		print("Response ends")
		print("-------------")
		print("Text of the response starts")
		print(type(r.text))
		print(f"r.text: '{r.text.strip()}'")
		print("Text of the response ends")

		log = print_log("* Response: " + r.text.strip(), log)
		#json_data = json.loads(r.text)
		text = r.text.strip()
		try:
			json_data = json.loads(text)
		except Exception:
			json_data = json.loads('')
			print(Exception)

		#json_data = json.loads(r.content.decode('utf-8'))
		# get url, which comes in the message
		log = print_log("* Status is: " + json_data['status'], log)
		# if success/url
		if json_data['status'] == "Success":
			url = json_data['message']
			# build html export
			result = build_html_report(url)
			# write to HTML file
			write_report(result, xdiff_rpt_fn, dir_edit)
			# log to myself
			log = print_log(f"* Link to xDiff report saved at: {os.path.join(dir_edit, xdiff_rpt_fn)}", log)
			send_email(log, subj + ' (admin)', receivers = [])
			
			# update PMs
			log4pm = print_log("A new xDiff report has been created:", log4pm)
			log4pm = print_log(f"\n* Report's URL: {str(url)}", log4pm)
			log4pm = print_log(f"\n* Link to xDiff report saved at: {denormalize_path(os.path.join(dir_edit, xdiff_rpt_fn))}", log4pm)

			receivers = get_recipients(pm_emails_path)
			send_email(log4pm, subj, receivers)
		else:
			log = print_log("* ERROR: URL to xDiff report not available.", log)
			send_email(log, "ERROR: URL not available", receivers = [])

	else:
		log = print_log("* OMT file missing or more than one OMT file in the folder.\nFiles compared are {} and {}".format(dir_orig, dir_edit), log)
		log = print_log("ERROR: Execution interrupted.", log)
		send_email(log, "ERROR: files not found", receivers = [])


	write_log(log, dir_edit, timestamp)




# REFERENCES

# https://2.python-requests.org//en/latest/user/quickstart/#post-a-multipart-encoded-file
# https://2.python-requests.org//en/latest/user/advanced/#advanced

import os, sys
from common import denormalize_path
from common import get_config_params

# paths relative to this file
parent_dir = os.path.dirname(os.path.abspath(__file__))
grandpa_dir = os.path.dirname(parent_dir)
creds_path = os.path.join(grandpa_dir, 'email', 'creds.txt')
pm_emails_path = os.path.join(grandpa_dir, 'email', 'receivers_pm.txt')
params_path  = os.path.join(grandpa_dir, 'config', 'params.txt')

# expects one line such as: username:password
with open(creds_path, 'r') as f:
	creds = f.read()

u, p = creds.strip().split(":")

print(u, p)

with open(pm_emails_path, 'r') as f:
	pms = set(l.strip() for l in f.readlines() if not l.startswith('#'))

print(pms)

path= "/media/data/data/company/bla/foo/bar"
print(denormalize_path(path))

def get_config_params(file_path):
	''' Gets key=value text file and returns dictionary with parameters '''
	with open(file_path) as f:
		return dict(l.strip().split("=") for l in f.readlines())


# Now access them as params["var1"].
# If the names are all valid python variable names, you can put this below:
	
#names = type("Names", [object], params)
params = get_config_params(params_path)
print(params)

diff_api_url = params['xdiff_url']
print(diff_api_url)

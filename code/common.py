def get_recipients(file_path):
	''' Expects a text file with one email per line'''
	with open(file_path, 'r') as f:
		return list(l.strip() for l in f.readlines() if not l.startswith('#'))


# turn PM's relative Windows paths to absolute Linux paths
def normalize_path(str):
	#return str.replace("\\", "/")
	return (str.replace("\\", "/")).replace('U:/', '/media/data/data/company/')


# turn absolute Linux paths to PM's relative Windows paths
def denormalize_path(str):
	#return str.replace("\\", "/")
	return str.replace('/media/data/data/company/', 'U:/').replace("/", "\\")


def get_config_params(file_path):
	''' Gets key=value text file and returns dictionary with parameters '''
	with open(file_path) as f:
		return dict(l.strip().split("=") for l in f.readlines())
# python3 -m pip3 install pandas yattag datetime pyinotify openpyxl xlrd
#from openpyxl import load_workbook
import pandas as pd
from pprint import pprint
#pp = pprint.PrettyPrinter(indent=4)
import os, sys, re
import os.path
from os import path
import glob
import difflib

#dir_edit = "../Lab/4_CODING_GUIDES/04_VERIF_reviewed_delivered/"
# Assign spreadsheet filename to `file`
#file = dir_edit + "_Tech/" + "200129_Steps_for_Difference_Reports.xlsx" # local
#file_with_paths = "200129_Steps_for_Difference_Reports.xlsx" # server



def repl_ph(path_templ, root): # repl_ph
	regex = re.compile(r'\[[^\]]+\]|xxx-XXX')
	return re.sub(regex, '*', path_templ.replace('{root}', root))


def expand_path(path_templ):
	return glob.glob(path_templ)


def get_path_templates(file):

	xl = pd.ExcelFile(file) # type: <class 'pandas.io.excel._base.ExcelFile'>

	if not 'config' in xl.sheet_names or not 'paths' in xl.sheet_names:
		print(f"The paths sheet or the config sheet not found")
		return None
	else:
		# get config: root and tasks
		config_sheet = xl.parse('config')
		config_dict = dict(zip(config_sheet['placeholder'], config_sheet['values']))
		root = config_dict['root']

		paths_sheet = xl.parse('paths')
		path_template_pairs = tuple(zip(paths_sheet['Path template to package 1'], paths_sheet['Path template to package 2']))

		#z = set((repl_ph(pair[0], root), repl_ph(pair[1], root)) for pair in path_template_pairs)
		path_templ_list = [{'orig': repl_ph(pair[0], root), 'edit': repl_ph(pair[1], root)} for pair in path_template_pairs]

		# remove duplicates
		uniq_path_templ_list = [dict(t) for t in {tuple(d.items()) for d in path_templ_list}]
		return uniq_path_templ_list


#pprint(get_paths(file_with_paths))

def get_diff_betwn_2_strs(str1, str2):
	return ''.join([li for li in difflib.ndiff(str1, str2) if li[0] != ' '])


def all_paths_paired_correctly(path_template_pairs, orig_paths, edit_paths):
	templ_diff = get_differece_between_two_strings(path_template_pairs['orig'], path_template_pairs['edit'])

	for orig_path, edit_path in zip(orig_paths, edit_paths):
		inst_diff = get_differece_between_two_strings(orig_path, edit_path)
		try:
			assert templ_diff == inst_diff
			print(">>> Identical difference between templates and instances")
			return True
		except AssertionError:
			print(">>> Different difference between templates and instances")
			print(AssertionError)
			return False


def equal_length(orig_paths, edit_paths):
	return len(orig_paths) == len(edit_paths)


def integrity_checks_pass(path_pair_tmpl):
	'''
	Function that takes a list of path template pairs, expands it to all their instances,
	and checks that all the path instance pairs are proper, comparing the difference between
	the two templates with the difference between every instances, which should be the same.
	If a path is missing in the server, one of these checks will fail. Functional and clean.
	'''
	orig_paths = expand_path(path_pair_tmpl['orig']) # list
	edit_paths = expand_path(path_pair_tmpl['edit']) # list

	# difference betweeen the two path templates
	tmpl_diff = get_diff_betwn_2_strs(path_pair_tmpl['orig'], path_pair_tmpl['edit'])
	# list of unique differences between all the two path instances
	diff_set = set([get_diff_betwn_2_strs(*i) for i in zip(orig_paths, edit_paths)])
	# get the first unique difference, which should also be the only one (check 2)
	inst_diff = next(iter(diff_set))

	check1 = tmpl_diff == inst_diff
	check2 = len(diff_set) == 1
	check3 = equal_length(orig_paths, edit_paths)

	return check1 and check2 and check3 # True if all are True


def get_path_instance_pairs(path_template_pairs):
	path_pair_inst_dict = dict()
	for path_pair_tmpl in path_template_pairs:
		if integrity_checks_pass(path_pair_tmpl):
			orig_paths = expand_path(path_pair_tmpl['orig']) # list
			edit_paths = expand_path(path_pair_tmpl['edit']) # list
			path_pair_inst_dict.update(dict(zip(orig_paths, edit_paths)))

	return path_pair_inst_dict


def get_folder_paths(path_to_config):

	if not os.path.exists(path_to_config):
		print(f"path_to_config '{path_to_config}' does not exist")
		return None

	#print(f"Getting paths from '{path_to_config}'")
	
	path_template_pairs = get_path_templates(path_to_config)
	path_instance_pairs = get_path_instance_pairs(path_template_pairs)
	paths = [{'orig': key, 'edit': value} for key, value in path_instance_pairs.items()]
	return paths


#pprint(get_folder_paths(path_to_ft))
# Emel:
# one
# changes to the Excel file need to be notified to Manuel
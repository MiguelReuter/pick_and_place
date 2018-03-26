# encoding : utf-8

import argparse
import json
import os
import re

def _init_parser():
	"""
	Create parser with specific arguments.

	output :
		- parser
	"""
	
	_parser = argparse.ArgumentParser()
	_parser.add_argument("--pull", help="pull scripts from UR3", action="store_true")
	_parser.add_argument("--create", help="create data base from script files", action="store_true")
	_parser.add_argument("--clear", help="clear all data base", action="store_true")
	return _parser

def pull_scripts(user="root", address="10.0.0.2", path="/programs/learned_objects/"):
	"""
	get URScripts from robot and copy its in learned_objects_scripts/ .
	"""

	path = path[:-1] if path[-1] == "/" else path
	command = 'scp {}@{}:{} learned_objects_scripts/'.format(user, address, path)
	os.system(command)


def create_data_base():
	"""
	create data base and construct all json files from URScripts.

	This function creates a json file only if it's not present in objects_models/ yet.
	"""

	script_files = []
	json_files = []
	
	# get script files list
	for file in os.listdir("learned_objects_scripts/"):
		if file.endswith(".script"):
			script_files.append(file)

	# get json files list
	for file in os.listdir("object_models/"):
		if file.endswith(".json"):
			json_files.append(file)
	
	# create json file for new objects
	model_created = False
	for file in script_files:
		if "{}.json".format(file[:-7]) not in json_files:
			with open("object_models/{}.json".format(file[:-7]), 'w') as outfile:
				obj_model = object_script_to_model("learned_objects_scripts/" + file)
				json.dump(obj_model, outfile)
				model_created = True
				print("model created for", file)
	if not model_created:
		print("data base is already up to date")

def _reg_catch(reg_ex, text, group_id=1):
	"""
	return a specific string in content with regular expression.

	input:
		- reg_ex [str] : raw regular expression
		- text [str] : content in which _re has to be founded
		- group_id [int] : precise which group has to be catch in reg_ex
	output:
		- [str] result of reg_ex or None if reg_ex not founded
	"""

	match = re.search(reg_ex, text)
	if match:
		return match.group(group_id)
	else:
		return None


def object_script_to_model(path):
	"""
	load a specific UR script file and generate an object model.

	The script file is a program from UR which :
		- recognize an object
		- move close to the object
		- pick the object
		- retract the object	
	input :
		- path [str] : filename of URScript to convet in json file.
	return :
		- object_model [dict]. Dict of string who represents the object.
	"""

	object_model = {"name": None,
					"vision_model": None,
					"is_ignore_orientation": None,
					"teaching_position": None,
					"new_snapshot_pos": None,
					"new_snapshot_pos_inv": None,
					"current_speed_0_thr": None,
					"current_force_0_thr": None,
					"move_approach": None,
					"move_pick": None,
					"move_retract": None}

	_name = re.search(r'(?:\\|\/)(.*)\.script', path)
	object_model["name"] = "object" if not _name else _name.group(1)

	# re patterns
	_re_6_fl_list = r'\[(?:-?\d*\.?\d*E?-?\d+,? ?){6}\]' 	# re for list of 6 signed float
	_re_vision_model = r'(?m)^\s*f = xmlrpc_server\.findmodel\(\"(\{[\w-]+\})", tool\[0\], tool\[1\], tool\[2\], tool\[3\], tool\[4\], tool\[5\]\)'
	_re_is_ignore_orientation = r'(?m)^\s*is_ignore_orientation = ((?:True)|(?:False))'
	_re_teaching_pos = r'(?m)^\s*object_teaching_location = p({})'.format(_re_6_fl_list)
	_re_new_snapshot_pos = r'(?m)^\s*snapshot_pos = pose_trans\(object_location, pose_trans\(pose_inv\(p({})\), p({})\)\)'.format(_re_6_fl_list, _re_6_fl_list)
	_re_current_speed_0_thr = r'(?m)^\s*if \(current_speed\[0\] != (-?\d*\.?\d*)\):'
	_re_current_force_0_thr = r'(?m)^\s*if \(current_force\[0\] != (-?\d*\.?\d*)\):'

	_re_move_approach = r'(?m)^\s*\$ \d+ "Rel_approach"\s+movel\(pose_trans\(snapshot_pos, p({})\), a=(?:-?\d*\.?\d*), v=(?:-?\d*\.?\d*)\)'.format(_re_6_fl_list)
	_re_move_pick = r'(?m)^\s*\$ \d+ "Rel_pick"\s+movel\(pose_trans\(snapshot_pos, p({})\), a=(?:-?\d*\.?\d*), v=(?:-?\d*\.?\d*)\)'.format(_re_6_fl_list)
	_re_move_retract = r'(?m)^\s*\$ \d+ "Rel_retract"\s+movel\(pose_trans\(snapshot_pos, p({})\), a=(?:-?\d*\.?\d*), v=(?:-?\d*\.?\d*)\)'.format(_re_6_fl_list)


	with open(path, "r") as file:
		content = file.read()
		camera_locate_match = re.search(r'\s*\$ \d+ "Camera Locate"', content)
		content = content[camera_locate_match.start():]
		
		object_model["vision_model"] = _reg_catch(_re_vision_model, content)
		object_model["is_ignore_orientation"] = _reg_catch(_re_is_ignore_orientation, content)
		object_model["teaching_position"] = _reg_catch(_re_teaching_pos, content)
		object_model["new_snapshot_pos_inv"] = _reg_catch(_re_new_snapshot_pos, content)
		object_model["new_snapshot_pos"] = _reg_catch(_re_new_snapshot_pos, content, 2)
		object_model["current_speed_0_thr"] = _reg_catch(_re_current_speed_0_thr, content)
		object_model["current_force_0_thr"] = _reg_catch(_re_current_force_0_thr, content)
		object_model["move_approach"] = _reg_catch(_re_move_approach, content)
		object_model["move_pick"] = _reg_catch(_re_move_pick, content)
		object_model["move_retract"] = _reg_catch(_re_move_retract, content)
	return object_model


def clear_data_base():
	"""
	clear data base and remove all json files in object_models/ .
	"""

	command = 'rm object_models/*.json'
	os.system(command)
	print("data base cleared")


if __name__ == "__main__":
	args = _init_parser().parse_args()

	if args.pull:
		pull_scripts()
	if args.create:
		create_data_base()
	if args.clear:
		clear_data_base()





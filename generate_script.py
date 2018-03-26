# encoding : utf-8

import argparse
import json
import os
import re


target_pos = {'A': [0., 0.3],
			  'B': [0.3, 0.]}


def _init_parser():
	"""
	Create parser with specific arguments.

	output :
		- parser
	"""
	
	_parser = argparse.ArgumentParser()
	_parser.add_argument("-o", help="specify which object to move", type=str)	
	_parser.add_argument("-p", help="specify the final emplacement", type=str)	
	_parser.add_argument("--push", help="push the generated script into UR", action="store_true")

	return _parser


def _str_list_to_list(str_l):
	"""
	convert a string representation of a list to a list of float.

	ex : '[0.1, 5.0]' --> [0.1, 5.0]

	input :
		- str_l [str] : string representation of a list of floats
	output :
		- l [list of floats] : list of floats from str_l
	"""
	str_l = str_l[1:-1]
	l = str_l.split(',')
	l = [float(i) for i in l]
	
	return l


def load_object_model(path):
	"""
	load a json file from specific path.

	input :
		- path [str]
	output :
		- result of json.load()
	"""
	with open(path, 'r') as file:
		return json.load(file)


def generate_script(obj_model, target_pos):
	"""
	generate an URScript from specific object model (from json file) and a specific target position.

	input:
		- obj_model [dict with string keys and string values] : represents the object from json file
		- target_pos [list of 2 floats] : x and y coordinates for desired target object position
	output :
		content [str] : content of URScript generated.
	"""

	with open("template_pick_and_place.script", 'r') as file:
		content = file.read()
		
		# replacing model object data in script
		for key in obj_model:
			_regex = r'<value_{}>'.format(key)
			content = re.sub(_regex, obj_model[key], content)
			
		# p<value_target_move_approach>
		_regex = r'<value_target_move_approach>'
		
		_snapshot_pos = _str_list_to_list(obj_model["new_snapshot_pos"])
		_approach_pos = _str_list_to_list(obj_model["move_approach"])
		target_approach_pose = [target_pos[0], target_pos[1], _snapshot_pos[2] - _approach_pos[2], 3.1415, 0.0, 0.0]			
		content = re.sub(_regex, "p" + target_approach_pose.__repr__(), content)

		# p<value_target_move_place>
		_regex = r'<value_target_move_place>'
		
		_place_pos = _str_list_to_list(obj_model["move_approach"])
		target_approach_pose = list(target_approach_pose)
		target_approach_pose[2] = _snapshot_pos[2] + _place_pos[2] + 0.05
		target_approach_pose[2] = 'object_location[2] + 0.01'
		pos_str = "p" + target_approach_pose.__repr__()
		pos_str = re.sub("'", "", pos_str)
		content = re.sub(_regex, pos_str, content)

		return content

def push_script(file, user="root", address="10.0.0.2", path="/programs/"):	
	"""
	send generated URScript to the robot.
	"""

	path = path[:-1] if path[-1] == "/" else path
	command = 'scp {} {}@{}:{}'.format(file, user, address, path)
	os.system(command)


if __name__ == "__main__":
	args = _init_parser().parse_args()

	# load specific object to move
	obj = load_object_model(args.o) if args.o else None
	pos = target_pos[args.p] if args.p else target_pos['A']
	
	if obj:
		output_script = generate_script(obj, pos)
		if output_script:
			path = "exported_scripts/{}_pos_{}.script".format(obj["name"], args.p)
			with open(path, 'w') as file:
				file.write(output_script)
				if args.push:
					push_script(path)
					






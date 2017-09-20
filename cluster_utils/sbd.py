#! /usr/bin/env python

import os
import re

def get_sbd_conf_file():
	file_list = [ '/etc/sysconfig/sbd', '/etc/default/sbd' ]
	for f in file_list:
		if os.path.exists(f):
			return f

	raise Exception('No SBD configuration file found')

def get_sbd_devices(conf_file):
	devices_regex = re.compile('^SBD_DEVICE=[\'\"]{0,1}(.+?)[\'\"]{0,1}$')
	with open(conf_file, 'r') as f:
		for line in f.readlines():
			rs = re.search(devices_regex, line)

			if rs:
				return rs.group(1).split(';')

def get_sbd_command_line():
	command_line = [ 'sbd' ]

	conf_file = get_sbd_conf_file()
	luns = get_sbd_devices(conf_file)

	if len(luns) == 0:
		raise('No device defined in %s' % conf_file)

	for lun in luns:
		command_line.append('-d')
		command_line.append(lun)

	if os.getuid() != 0:
		command_line.insert(0, 'sudo')

	return command_line

def sbd_reset_node(node, command_line = None):
	if command_line == None:
		command_line = get_sbd_command_line()

	reset_command = command_line
	reset_command.append('message')
	reset_command.append(node)
	reset_command.append('clear')

	return subprocess.check_call(command_line)

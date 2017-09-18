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


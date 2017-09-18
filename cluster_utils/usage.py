#! /usr/bin/env python

import os
import re
import subprocess

def get_running_machines():
	return int(subprocess.check_output("machinectl --no-pager --no-legend|wc -l", shell=True).strip())

def get_running_resources(node):
	if os.getuid() > 0:
		return None

	current_node = ""
	counter = -1
	node_status_regex = re.compile("^Node (\w+): (\w+)$")
	resource_regex = re.compile("^\s+(\d+)\s+.*$")

	for line in subprocess.check_output("crm_mon -Dnb1", shell=True).split('\n'):
		result = re.search(node_status_regex, line)
		if result:
			current_node = result.group(1)
			if current_node == node and counter > -1:
				return counter + 1
			if current_node != node and counter > 0:
				return counter + 1
		else:
			result = re.search(resource_regex, line)
			if result and current_node == node:
				counter += int(result.group(1))

	return None

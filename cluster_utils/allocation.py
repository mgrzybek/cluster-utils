#! /usr/bin/env python

import os
import re
import sys
import socket
import subprocess

def translate_range(x):
	result = []
	for part in x.split(','):
		if '-' in part:
			a, b = part.split('-')
			a, b = int(a), int(b)
			result.extend(range(a, b + 1))
		else:
			a = int(part)
			result.append(a)
	return result

def get_files(abs_path):
	result = []
	for root, dirs, files in os.walk(abs_path, topdown=False):
		for name in files:
			result.append("%s/%s" % (root , name))

	return result

def get_cpus_mapping_from_xml(path, cpus):
	cpuset_regex = re.compile("cpuset='(.*?)'")
	name_regex = re.compile("\<name\>(\w+)<\/name\>")
	xml_regex = re.compile("\.xml$")

	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			if re.search(xml_regex, name):
				xml = "%s/%s" % (root , name)
				domain_name = ""

				for line in open(xml, 'r').readlines():
					name_extract = re.search(name_regex, line)
					cpuset_extract = re.search(cpuset_regex, line)

					if name_extract != None:
						domain_name = name_extract.group(1)

					if cpuset_extract != None:
						for cpu in translate_range(cpuset_extract.group(1)):
							cpus[cpu] = domain_name
						return True
	return False

def init_cpus(cpus):
	server_cpus = int(subprocess.check_output("cat /proc/cpuinfo|grep -c ^proc", shell=True).strip())

	for i in range(0, server_cpus):
		cpus[i] = ''

def get_cpus_mapping_from_machine_xml(cpus):
	found_machines = False

	for machine in get_files('/etc/pacemaker'):
		found_machines = True
		get_cpus_mapping_from_xml(machine, cpus)

	if found_machines == False:
		raise

def get_cpus_mapping_from_machine_slice(cpus):
	reg_lxc_machine = re.compile('\/sys\/fs\/cgroup\/cpuset\/machine\.slice\/machine-lxc.{4}(\w+)\.scope/cpuset.cpus$')

	# Get the cpus range for machine.slice
	for cpu in translate_range(open('/sys/fs/cgroup/cpuset/machine.slice/cpuset.cpus', 'r').read()):
		if cpu not in cpus:
			cpus[cpu] = ''

	# Get the cpus range for each machine
	for machine in get_files('/sys/fs/cgroup/cpuset/machine.slice'):
		if re.search("cpuset.cpus$", machine) and not machine == '/sys/fs/cgroup/cpuset/machine.slice/cpuset.cpus':
			rs = reg_lxc_machine.search(machine)

			if rs:
				for cpu in translate_range(open(machine, 'r').read()):
					cpus[cpu] = rs.group(1)

def get_cpus_from_crm_attributes(cpus, quiet):
	if os.getuid() > 0:
		if quiet == False:
			print("cannot get crm attributes, must be run as root")
		return

	crm_cmd = "/usr/sbin/crm node utilization %s show cpu" % socket.gethostname()
	crm_cpus = int(subprocess.check_output(crm_cmd, shell=True).strip().split("=")[-1])

	server_cpus = int(subprocess.check_output("cat /proc/cpuinfo|grep -c ^proc", shell=True).strip())

	for i in range(0, server_cpus):
		if i < server_cpus - crm_cpus:
			cpus[i] = 'crm'

def get_cpus_mapping(cpus, quiet=True):
	try:
		get_cpus_mapping_from_machine_slice(cpus)
	except:
		pass

	try:
		get_cpus_mapping_from_machine_xml(cpus)

	except:
		pass

	try:
		get_cpus_from_crm_attributes(cpus, quiet)
	except:
		pass

def get_available_cpus(cpus):
	result = []
	for cpu in cpus:
		if cpus[cpu] == '':
			result.append(cpu)
	return result

def get_used_cpus(cpus):
	result = []
	for cpu in cpus:
		if cpus[cpu] != '':
			result.append(cpu)
	return result

def bytes_to_gigabytes(value):
	return int(value) / 1024 / 1024 / 1024

def megabytes_to_gigabytes(value):
	return int(value) / 1024

def get_files(abs_path):
	result = []
	for root, dirs, files in os.walk(abs_path, topdown=False):
		for name in files:
			result.append("%s/%s" % (root , name))

	return result

def get_mem_mapping_from_xml(path, mems):
	mem_regex = re.compile("\<memory unit='GiB'\>(\d+)\<\/memory\>")
	name_regex = re.compile("\<name\>(\w+)<\/name\>")
	xml_regex = re.compile("\.xml$")

	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			if re.search(xml_regex, name):
				xml = "%s/%s" % (root , name)
				domain_name = ""

				for line in open(xml, 'r').readlines():
					name_extract = re.search(name_regex, line)
					mem_extract = re.search(mem_regex, line)

					if name_extract != None:
						domain_name = name_extract.group(1)

					if mem_extract != None:
						for mem in translate_range(mem_extract.group(1)):
							mems[domain_name] = mem * 1048576
						return True
	return False

def get_mem_mapping_from_machine_xml(mems):
	found_machines = False

	for machine in get_files('/etc/pacemaker'):
		found_machines = True
		get_mem_mapping_from_xml(machine, mems)

	if found_machines == False:
		raise

def get_mem_mapping_from_machine_slice(mems):
	reg_lxc_machine = re.compile('\/sys\/fs\/cgroup\/memory\/machine\.slice\/machine-lxc.{4}(\w+)\.scope/memory.limit_in_bytes$')

	# Get the memory limit for machine.slice
	mems['machine.slice'] = bytes_to_gigabytes(open('/sys/fs/cgroup/memory/machine.slice/memory.limit_in_bytes', 'r').read())

	# Get the memory usage for each machine
	for machine in get_files('/sys/fs/cgroup/memory/machine.slice'):
		if re.search("memory.limit_in_bytes$", machine) and not machine == '/sys/fs/cgroup/memory/machine.slice/memory.limit_in_bytes':
			rs = reg_lxc_machine.search(machine)

			if rs:
					mems[rs.group(1)] = bytes_to_gigabytes(open(machine, 'r').read())

def get_mem_from_crm_attributes(mems):
	if os.getuid() > 0:
		if quiet == False:
			print("cannot get crm attributes, must be run as root")
		return

	crm_cmd = "/usr/sbin/crm node utilization %s show hv_memory" % socket.gethostname()
	mems['machine.slice'] = megabytes_to_gigabytes(subprocess.check_output(crm_cmd, shell=True).strip().split("=")[-1])

def get_mem_mapping(mems):
	try:
		get_mem_mapping_from_machine_slice(mems)
	except:
		pass

	try:
		get_mem_mapping_from_machine_xml(mems)
		get_mem_from_crm_attributes(mems)
	except:
		pass

def get_available_mems(mems):
	return mems['machine.slice'] - get_used_mems(mems)

def get_used_mems(mems):
	used = 0

	for domain in mems:
		if not domain == 'machine.slice':
			used += mems[domain]

	return used

def set_cpuset_exclusive(path):
	_path = "%s/cpuset.cpu_exclusive" % path
	with open(_path, 'w') as f:
		f.write("1")

def unset_cpuset_exclusive(path):
	_path = "%s/cpuset.cpu_exclusive" % path
	with open(_path, 'w') as f:
		f.write("0")

def set_cpuset(path, cpuset):
	_path = "%s/cpuset.cpus" % path
	with open(_path, 'w') as f:
		f.write(cpuset)

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "cluster-utils",
	version = "1.1.3",
	author = "Mathieu Grzybek",
	author_email = "mathieu@grzybek.fr",
	description = "Utilitaires pour la gestion des ressources",
	license = "GPLv3",
	keywords = "monitoring pacemaker, libvirtd & cgroups",
	url = "https://git.gendarmerie.fr/stig/cluster-utils",
	packages = ['cluster_utils'],
	scripts = [ 'bin/cluster_set_cpuset', 'bin/cluster_get_cpuset_allocation', 'bin/cluster_get_mem_allocation', 'bin/cluster_get_cluster_usage', 'bin/sbd_list', 'bin/sbd_dump' ],
	install_requires = [''],
	long_description = read('README'),
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Topic :: Utilities",
		"Environment :: Console",
		"License :: OSI Approved :: GPLv3 License"
	],
)

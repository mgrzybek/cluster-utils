# cluster-utils
Tools to manage clustered environment.

## cgroups tools

* cluster_get_cluster_usage: gives the running pacemaker resources and the number of running virtual
machines using machinectl.

* cluster_get_cpuset_allocation: gives the usage of the CPUS, according to machines.slice's cgroup configuration
and libvirt XML files.

* cluster_get_mem_allocation: gives the usage of the RAM, according to machines.slice's cgroup configuration
and libvirt XML files.

* cluster_set_cpuset: updates the cpuset properties of the given cgroup path.

## sbd tools

The available scripts are used to manage STONITH-Based Devices. They are wrappers to get the device-list directly.

* sbd_list: [sudo] sbd [-d device]+ list

* sbd_dump: [sudo] sbd [-d device]+ dump

* sbd_reset_node: clears the nodes marked as reset

echo "Removing Interfaces ..."
neutron router-interface-delete osm-router subnet=subnet-mgmt
echo "removing networks"
openstack network delete mgmt
openstack network delete tag1
openstack network delete tag2
openstack network delete tag3
openstack network delete tag4

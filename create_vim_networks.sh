source OSM-openrc.sh 


echo "Creating networks ..."
echo "Creating Mgmt network ..."
neutron net-create mgmt --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=513 --shared 
neutron subnet-create --name subnet-mgmt mgmt 10.208.0.0/24 --allocation_pool start=10.208.0.2,end=10.208.0.254

echo "Creating tag1 network ..."
neutron net-create tag1 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=231 --shared 
neutron subnet-create --name subnet-tag1 tag1 10.13.1.0/24 --allocation_pool start=10.13.1.2,end=10.13.1.254

echo "Creating tag2 network ..."
neutron net-create tag2 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=232 --shared 
neutron subnet-create --name subnet-tag2 tag2 10.13.2.0/24 --allocation_pool start=10.13.2.2,end=10.13.2.254

echo "Creating tag3 network ..."
neutron net-create tag3 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=233 --shared 
neutron subnet-create --name subnet-tag3 tag3 10.13.3.0/24 --allocation_pool start=10.13.3.2,end=10.13.3.254

echo "Creating tag4 network ..."
neutron net-create tag4 --provider:network_type=vlan --provider:physical_network=public --provider:segmentation_id=234 --shared 
neutron subnet-create --name subnet-tag4 tag4 10.13.4.0/24 --allocation_pool start=10.13.4.2,end=10.13.4.254

# With floating IP adreess or no
sudo osm --hostname 192.168.100.24 vim-create --name osm-group13 --user osm --password osm --tenant OSM --auth_url $OS_AUTH_URL --account_type openstack --config '{security_groups: default, keypair: osm-kp}'

mac1=$(echo grupo13mac|md5sum|sed 's/^\(..\)\(..\)\(..\)\(..\)\(..\).*$/02:\1:\2:\3:\4:\5/')

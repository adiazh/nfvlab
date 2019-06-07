echo "Creating project OSM"

openstack project create --description "OSM" OSM --domain default --or-show

echo "Creating user \"osm\" and add it as admin to project OSM"
openstack user create --project OSM --password osm --description "osm user" osm --or-show 
OSM_TENANT_ID=`openstack project list | grep OSM | cut -f2 -d "|" | sed 's/ //g'`
openstack role add --user osm --project OSM admin
openstack role assignment list --user osm --project $OSM_TENANT_ID --names

echo "Rename ubuntu image name to ubuntu:16.04"

openstack image set --name ubuntu:16.04 ubuntu-16.04-server-cloudimg-amd64-disk1


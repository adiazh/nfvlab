echo "Creating project OSM"
openstack project create --description "OSM" OSM --domain default


echo "Creating user "osm" and add it as admin to project OSM"
openstack user create --project OSM --password osm osm
OSM_TENANT_ID=`openstack project list | grep OSM | cut -f2 -d "|" | sed 's/ //g'`
openstack role add --user osm --project OSM admin
openstack role assignment list --user osm --project $OSM_TENANT_ID --names




 openstack project create --description OSM OSM --or-show

 openstack user create --project OSM --password osm --description osm osm --or-show

 openstack keypair create osm-kp > dev/config/osm-kp.pem

 openstack image set --name ubuntu:16.04 ubuntu-16.04-server-cloudimg-amd64-disk1

 
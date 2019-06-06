echo "deploying descriptiors in OSM" 

osm vnfd-create web_juju_vnf.tar.gz 

osm nsd-create monojuju-VM_ns.tar.gz

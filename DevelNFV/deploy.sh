echo "deploying descriptiors in OSM" 

osm vnfd-create webserver_vnf.tar.gz 

osm nsd-create mono-VM_ns.tar.gz

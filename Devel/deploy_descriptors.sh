echo "deploying descriptiors in OSM" 

#osm vnfd-create webserver_vnf.tar.gz 
osm --hostname 192.168.100.24 vnfd-create web_vnf_vnfd.tar.gz 
#osm nsd-create multi-VM_ns.tar.gz
osm --hostname 192.168.100.24 nsd-create singleWebServer_ns_nsd.tar.gz
#osm nsd-create mono-VM_ns.tar.gz

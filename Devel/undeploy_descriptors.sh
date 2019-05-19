echo "deploying descriptiors in OSM" 

osm --hostname 192.168.100.24 nsd-delete singleWebServer_ns_nsd
#osm vnfd-create webserver_vnf.tar.gz 
sleep 3

osm --hostname 192.168.100.24 vnfd-delete web_vnf_vnfd
#osm nsd-create multi-VM_ns.tar.gz

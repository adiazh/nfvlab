#export PATH=$PATH:/usr/share/osm-devops/descriptor-packages/tools/

echo "Validating Descriptors ..."
validate_descriptor.py webserver_vnf/webserver_vnfd.yaml
#validate_descriptor.py multi-VM_ns/multi-VM_nsd.yaml 
validate_descriptor.py mono-VM_ns/mono-VM_nsd.yaml
#validate_descriptor.py web_vnf_vnfd/web_vnf_vnfd.yaml 
#validate_descriptor.py singleWebServer_ns_nsd/singleWebServer_ns_nsd.yaml 

sleep 1

echo "Generating Packages ..."
generate_descriptor_pkg.sh -v -N -t vnfd webserver_vnf/
generate_descriptor_pkg.sh -v -N -t nsd mono-VM_ns/
#generate_descriptor_pkg.sh -v -N -t nsd multi-VM_ns/
#generate_descriptor_pkg.sh -v -N -t vnfd web_vnf_vnfd
#generate_descriptor_pkg.sh -v -N -t nsd singleWebServer_ns_nsd/


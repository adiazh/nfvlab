#export PATH=$PATH:/usr/share/osm-devops/descriptor-packages/tools/

validate_descriptor.py webserver_vnf/webserver_vnfd.yaml 
validate_descriptor.py multi-VM_ns/multi-VM_nsd.yaml 
validate_descriptor.py mono-VM_ns/mono-VM_nsd.yaml 

generate_descriptor_pkg.sh -v -N -t vnfd webserver_vnf/
generate_descriptor_pkg.sh -v -N -t nsd mono-VM_ns/
generate_descriptor_pkg.sh -v -N -t nsd multi-VM_ns/


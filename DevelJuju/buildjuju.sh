#export PATH=$PATH:/usr/share/osm-devops/descriptor-packages/tools/

echo "Validating Descriptors ..."
validate_descriptor.py web_juju_vnf/web_juju_vnfd.yaml
validate_descriptor.py monojuju-VM_ns/monojuju-VM_nsd.yaml

sleep 1

echo "Generating Packages ..."
generate_descriptor_pkg.sh -v -N -t vnfd web_juju_vnf/
generate_descriptor_pkg.sh -v -N -t nsd monojuju-VM_ns/


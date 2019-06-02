#!/usr/bin/env python
"""
vlanhost.py: Host subclass that uses a VLAN tag for the default interface.

Dependencies:
    This class depends on the "vlan" package
    $ sudo apt-get install vlan

Usage (example uses VLAN ID=1000):
    From the command line:
        sudo mn --custom vlanhost.py --host vlan,vlan=1000

    From a script (see exampleUsage function below):
        from functools import partial
        from vlanhost import VLANHost

        ....

        host = partial( VLANHost, vlan=1000 )
        net = Mininet( host=host, ... )

    Directly running this script:
        sudo python vlanhost.py 1000

"""

from mininet.node import Host
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.log import error


class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        #intf.name = newName
        # add VLAN interface to host's name to intf map
        #self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }


# pylint: disable=arguments-differ

class LabSetup ( Topo ):
    def build (self, webip='10.13.1.3/24', mac='02:61:fb:eb:25:a2'):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        vm1 = self.addHost ('w1', cls=VLANHost, vlan=231, ip=webip, mac=mac )
        vm2 = self.addHost ('w2', cls=VLANHost, vlan=232, ip=webip, mac=mac)
        vm3 = self.addHost ('w3', cls=VLANHost, vlan=233, ip=webip, mac=mac)
        vm4 = self.addHost ('w4', cls=VLANHost, vlan=234, ip=webip, mac=mac)
        juju1 = self.addHost ('juju1', cls=VLANHost, vlan=513, ip='10.208.0.11')
        juju2 = self.addHost ('juju2', cls=VLANHost, vlan=513, ip='10.208.0.12')
        client = self.addHost ('client', ip = '10.13.1.10/24', mac='02:cc:d8:7f:ff:93')
        lap = self.addHost ('lap', ip = '172.16.24.209/23')
        mport = self.addHost ('mport', ip = '172.16.24.211/23')
        self.addLink( s1, s2 )
        self.addLink( s1, mport )
        self.addLink( s1, juju1 )
        self.addLink( s1, vm1 )
        self.addLink( s1, vm2 )
        self.addLink( s1, vm3 )
        self.addLink( s1, vm4 )
        self.addLink( s2, lap )
        self.addLink( s2, client )
        self.addLink( s2, juju2 )


def createLabTopo():
    """ Creates Lab SDN"""

    from mininet.node import RemoteController

    net = Mininet( topo=LabSetup(), controller=partial( RemoteController, ip='127.0.0.1', port=6633 ))
    #net.addController(name='ryu', controller=cont)
    net.start()
    CLI( net )
    net.stop()


if __name__ == '__main__':
    import sys
    from functools import partial
    from mininet.net import Mininet
    from mininet.cli import CLI
    from mininet.topo import SingleSwitchTopo
    from mininet.log import setLogLevel

    setLogLevel( 'info' )

    createLabTopo()

# arp -s arp -s 10.13.1.10 02:cc:d8:7f:ff:93
# arp -s arp -s 10.13.1.3 02:61:fb:eb:25:a2

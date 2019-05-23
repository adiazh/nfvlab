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

class VLANStarTopo( Topo ):
    """Example topology that uses host in multiple VLANs

       The topology has a single switch. There are k VLANs with
       n hosts in each, all connected to the single switch. There
       are also n hosts that are not in any VLAN, also connected to
       the switch."""

    def build( self, k=3, n=4, vlanBase=230 ):
        s1 = self.addSwitch( 's1' )
        for i in range( k ):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % ( j+1, vlan )
                h = self.addHost( name, cls=VLANHost, vlan=vlan )
                self.addLink( h, s1 )
        for j in range( n ):
            h = self.addHost( 'h%d' % (j+1) )
            self.addLink( h, s1 )

class LabSetup ( Topo ):
    def build (self, webip='10.213.1.1', mac='02:00:00:00:00:00'):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        vm1 = self.addHost ('w1', cls=VLANHost, vlan=231)
        vm2 = self.addHost ('w2', cls=VLANHost, vlan=231)
        vm3 = self.addHost ('w3', cls=VLANHost, vlan=231)
        vm4 = self.addHost ('w4', cls=VLANHost, vlan=231)
        juju1 = self.addHost ('juju1', cls=VLANHost, vlan=513)
        juju2 = self.addHost ('juju2', cls=VLANHost, vlan=513)
        client = self.addHost ('client')
        laptop = self.addHost ('laptop')
        mport = self.addHost ('mport')
        self.addLink( s1, s2 )
        self.addLink( s1, mport )
        self.addLink( s1, juju1 )
        self.addLink( s2, laptop )
        self.addLink( s2, client )
        self.addLink( s2, juju2 )



def exampleCustomTags():
    """Simple example that exercises VLANStarTopo"""

    net = Mininet( topo=VLANStarTopo())
    cont=partial( RemoteController, ip='127.0.0.1', port=6633 )
    net.addController(self, name='ryu', controller=cont)
    net.start()
    CLI( net )
    net.stop()

def createLabTopo():
    """Simple example that exercises VLANStarTopo"""

    from mininet.node import RemoteController

    net = Mininet( topo=LabSetup() )
    cont=partial( RemoteController, ip='127.0.0.1', port=6633 )
    net.addController(name='ryu', controller=cont)
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

#    if not quietRun( 'which vconfig' ):
#        error( "Cannot find command 'vconfig'\nThe package",
#               "'vlan' is required in Ubuntu or Debian,",
#               "or 'vconfig' in Fedora\n" )
#        exit()


    #exampleCustomTags()
    createLabTopo()

import inspect
import os
import atexit
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.topo import SingleSwitchTopo
from mininet.node import RemoteController


net = None

class FVTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
	h1 = self.addHost( 'h1' )
	h2 = self.addHost( 'h2' )
	h3 = self.addHost( 'h3' )
	h4 = self.addHost( 'h4' )
	s1 = self.addSwitch( 's1' )
	s2 = self.addSwitch( 's2' )
	# Add links
	self.addLink( h1, s1 )
	self.addLink( h2, s1 )
	self.addLink( h3, s1 )
	self.addLink( s1, s2 )
	self.addLink( s2, h4 )      

    
    
        info( '\n*** printing and validating the ports running on each interface\n' )
        


def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink,listenPort=6633, autoSetMacs=True, controller=lambda name: RemoteController(name, ip='127.0.0.1'))

                 
    
    info('** Starting the network\n')
    net.start()


    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    if net is not None:
        info('** Tearing down Overlay network\n')
        net.stop()

if __name__ == '__main__':

    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()

topos = { 'mytopo': ( lambda: FVTopo() ) }


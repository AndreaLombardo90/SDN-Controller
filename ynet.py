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
    # credit: https://github.com/onstutorial/onstutorial/blob/master/flowvisor_scripts/flowvisor_topo.py
    
		
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 1}
        video_link_config = {'bw': 10}
        host_link_config = {}

        # Create switch nodes
        for i in range(6):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(4):
            self.addHost('h%d' % (i+1), **hconfig)

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue
        
        self.addLink('h1', 's1', port1=1, port2=2, **video_link_config)
        self.addLink('s1', 's2', port1=1, port2=1, **video_link_config)
        self.addLink('s2', 's3', port1=2, port2=1, **video_link_config)
        self.addLink('s2', 's5', port1=3, port2=1, **video_link_config)
        self.addLink('s3', 's4', port1=2, port2=1, **video_link_config)
        self.addLink('s5', 's6', port1=2, port2=1, **video_link_config)
        self.addLink('s4', 'h2', port1=2, port2=1, **video_link_config)
        self.addLink('s6', 'h2', port1=2, port2=2, **video_link_config)
        self.addLink('h3', 's5', port1=5, port2=5, **video_link_config)
        self.addLink('h4', 's6', port1=6, port2=6, **video_link_config)
        

	
    
        info( '\n*** printing and validating the ports running on each interface\n' )
        



def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633, autoSetMacs=True)
    ### Host h1
    interfaces = []
    actual_ip = 10
    
    for i in range(1,5):
      
      h1 = net.get("h"+str(i))
      interfaces = h1.intfList()
      
      for i in interfaces:
	h1.setIP("10.0.0." + str(actual_ip) + "/24", intf=i)
	actual_ip = actual_ip + 1	
                  
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


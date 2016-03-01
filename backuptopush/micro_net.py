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

        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        video_link_config = {'bw': 10}

        # Create switch nodes
        for i in range(4):
            sconfig = {'dpid': "1a:80:fd:4b:91:0" + str(i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(2):
            self.addHost('h%d' % (i+1), **hconfig)

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue
        video_link_config["bw"] = 10 
        self.addLink('h1', 's1', port1=1, port2=1, **video_link_config)
        video_link_config["bw"] = 20
        self.addLink('s1', 's2', port1=2, port2=2, **video_link_config)
        video_link_config["bw"] = 10
        self.addLink('s1', 's3', port1=3, port2=3, **video_link_config)        
        video_link_config["bw"] = 20
        self.addLink('s2', 's4', port1=4, port2=4, **video_link_config)        
        video_link_config["bw"] = 10
        self.addLink('s3', 's4', port1=5, port2=5, **video_link_config)                
        video_link_config["bw"] = 10
        self.addLink('s4', 'h2', port1=6, port2=6, **video_link_config)                

    
    
        info( '\n*** printing and validating the ports running on each interface\n' )
        


def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink,listenPort=6633, autoSetMacs=True, controller=lambda name: RemoteController(name, ip='127.0.0.1'))

                  
    ### Hosts MAC address configuration
    interfaces = []
    actual_mac = 20
    
    for i in range(1,3):
      
      h1 = net.get("h"+str(i))
      interfaces = h1.intfList()
      
      for i in interfaces:
	h1.setMAC("8a:a4:5c:95:3a:" + str(actual_mac), intf=i)
	actual_mac = actual_mac + 1	                  
    
    
    
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


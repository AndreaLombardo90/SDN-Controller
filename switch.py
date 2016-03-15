from port import Port

class Switch:
  def __init__(self, name):
    #switch identifier (dpid is equal to MAC address according to POX logic)
    self.dpid = name
    #switch ARP table implemented with a dictionary: MAC address as key and port(s) as value(s).
    self.ARPTable = {}
    #list of Port objects
    self.ports = []
    #switch map from port to destination DPID
    self.map_ports = {}
    
  def addPort(self, ifname, number, mac):
    p = Port(ifname, number, mac)
    self.ports.append(p)
    
  def addNeigh(self, port, neigh):
    self.map_ports[port] = neigh
    print("Aggiornato switch " + str(self.dpid) + " stato mappa " + str(self.map_ports) + "\n")
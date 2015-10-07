from port import Port

class Switch:
  def __init__(self, name):
    #switch identifier (dpid is equal to MAC address according to POX logic)
    self.dpid = name
    #switch ARP table implemented with a dictionary: MAC address as key and port(s) as value(s).
    self.ARPTable = {}
    #list of Port objects
    self.ports = []
    
  def addPort(self, ifname, number, mac):
    p = Port(ifname, number, mac)
    self.ports.append(p)
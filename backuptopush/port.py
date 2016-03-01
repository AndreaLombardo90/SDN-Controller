class Port:
  def __init__(self, ifn, num, mac):
     #interface name (like s1-eth1)
     self.ifname = ifn
     #port number
     self.number = num
     #mac address of this port
     self.mac = mac
    
    
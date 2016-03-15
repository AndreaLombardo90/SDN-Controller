import re
import datetime
import time

class Rule:
  '''
  Rule can be of three types:
  
  drop every packet coming from X_MAC/IP independently by his content:
  
  X_MAC/IP DROP
  
  drop every packet that has X_MAC/IP as source and Y_MAC/IP as destination independently by his content:
  
  FROM X_MAC/IP TO Y_MAC/IP DROP
  
  drop every packet originated  by X_MAC/IP with Y_MAC/IP as destination traveling on PROTOCOL:
  
  IF PROTOCOL FROM X_MAC/IP TO Y_MAC/IP DROP
  
  '''
  def __init__(self, rule_str):
    '''
    before we can instatiate the new rule, we must be sure that it respect one of the forms listed above

    case will be 0 if no valid rule can be extracted by rule_str, others values are:
    
    1 -> X_MAC/IP DROP
    
    2 -> FROM X_MAC/IP TO Y_MAC/IP DROP
    
    3 -> IF PROTOCOL FROM X_MAC/IP TO Y_MAC/IP	DROP
    
    '''
    
    case = 0
    
    #X_MAC/IP DROP
    explode = rule_str.split()
    pat_ip = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    pat_mac = re.compile(r'^([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})$', re.IGNORECASE)
    
    
    #rules that don't specify port(s)
    
    #rule of type: MAC/IP DROP
    if ((len(explode) == 3) and (str(explode[0]) == "FROM") and (pat_ip.match(explode[1]) or pat_mac.match(explode[1])) and (str(explode[2]) == "DROP")):
	case = 1

    #rule of type: FROM MAC/IP TO MAC/IP DROP	
    if (len(explode) == 5 and (pat_ip.match(explode[1]) or pat_mac.match(explode[1])) and (pat_ip.match(explode[3]) or pat_mac.match(explode[3])) and str(explode[0]) == "FROM" and str(explode[2]) == "TO" and str(explode[4]) == "DROP"):
	case = 2

    #rule of type: IF PROTOCOL FROM X DROP	
    if (len(explode) == 5):
      if (str(explode[0]) == "IF" and str(explode[2]) == "FROM" and str(explode[4]) == "DROP"):
	if ((pat_ip.match(explode[3]) or pat_mac.match(explode[3]))):
	  case = 3
	  
    #rule of type: IF PROTOCOL FROM X TO Y DROP      
    if (len(explode) == 7):
      if (str(explode[0]) == "IF" and str(explode[2]) == "FROM" and str(explode[4]) == "TO" and str(explode[6]) == "DROP"):
	if ((pat_ip.match(explode[3]) or pat_mac.match(explode[3])) and (pat_ip.match(explode[5]) or pat_mac.match(explode[5]))):
	  case = 4
	  
    #rules with port(s) specified
    
    #rule of type: MAC/IP PORT DROP
    if ((len(explode) == 3) and (pat_ip.match(explode[0]) or pat_mac.match(explode[0])) and (str(explode[2]) == "DROP")):
	case = 5

    #rule of type: FROM MAC/IP PORT TO MAC/IP DROP		
    if (len(explode) == 6 and (pat_ip.match(explode[1]) or pat_mac.match(explode[1])) and (pat_ip.match(explode[4]) or pat_mac.match(explode[4])) and str(explode[0]) == "FROM" and str(explode[3]) == "TO" and str(explode[5]) == "DROP"):
	case = 6

    #rule of type: FROM MAC/IP TO MAC/IP PORT DROP		
    if (len(explode) == 6 and (pat_ip.match(explode[1]) or pat_mac.match(explode[1])) and (pat_ip.match(explode[3]) or pat_mac.match(explode[3])) and str(explode[0]) == "FROM" and str(explode[2]) == "TO" and str(explode[5]) == "DROP"):
	case = 7	
	
    #rule of type: FROM MAC/IP PORT TO MAC/IP PORT DROP		
    if (len(explode) == 7 and (pat_ip.match(explode[1]) or pat_mac.match(explode[1])) and (pat_ip.match(explode[4]) or pat_mac.match(explode[4])) and str(explode[0]) == "FROM" and str(explode[3]) == "TO" and str(explode[6]) == "DROP"):
	case = 8		  
    
    
    #end check rules
      
    if case == 0:
      print "Rule not well-formed. Program terminated.\n"
      exit(1)
    
    
    #rule of type: FROM MAC/IP DROP
    if case == 1:
      self.rule_type = 1
      self.src = explode[1]
      self.dst = None
      self.protocol = None
      self.port1 = None
      self.port2 = None      
    
    #rule of type: FROM MAC/IP TO MAC/IP DROP
    if case == 2:
      self.rule_type = 2
      self.src = explode[0]
      self.dst = explode[3]
      self.protocol = None
      self.port1 = None
      self.port2 = None      
    
    #rule of type: IF PROTOCOL FROM X DROP
    if case == 3:
      self.rule_type = 3
      self.src = explode[3]
      self.dst = None
      self.port1 = None
      self.port2 = None       
      #check if protocol is supported
      if (explode[1] == "LLDP" or explode[1] == "DNS" or explode[1] == "DHCP" or explode[1] == "HTTP" or explode[1] == "FTP" or explode[1] == "UDP" or explode[1] == "TCP" or explode[1] == "IP" or explode[1] == "ICMP"):
	self.protocol = explode[1] 
      else:
	print "3Rule not well-formed. Protocol not recognized. Program terminated.\n"
	exit(1)	
    
    #rule of type: IF PROTOCOL FROM X TO Y DROP
    if case == 4:
      self.rule_type = 4
      self.src = explode[3]
      self.dst = explode[5]
      self.port1 = None
      self.port2 = None      
      #check if protocol is supported
      if (explode[1] == "LLDP" or explode[1] == "DNS" or explode[1] == "DHCP" or explode[1] == "HTTP" or explode[1] == "FTP" or explode[1] == "UDP" or explode[1] == "TCP" or explode[1] == "IP" or explode[1] == "ICMP"):
	self.protocol = explode[1] 
      else:
	print "4Rule not well-formed. Protocol not recognized. Program terminated.\n"
	exit(1)	   
    
    #rule of type: MAC/IP PORT DROP    
    if case == 5:
      self.rule_type = 5
      self.src = explode[0]
      self.dst = None
      self.protocol = None
      self.port2 = None
      if isinstance(explode[1], int):
	self.port1 = explode[1]     
      else:
	print "5Rule not well-formed. Invalid port. Program terminated.\n"
	exit(1)		
    
    #rule of type: FROM MAC/IP PORT TO MAC/IP DROP	     
    if case == 6:
      self.rule_type = 6
      self.src = explode[0]
      self.dst = explode[3]
      self.protocol = None
      self.port2 = None   
      if isinstance(explode[2], int):
	self.port1 = explode[2]     
      else:
	print "6Rule not well-formed. Invalid port. Program terminated.\n"
	exit(1)	      
      
    #rule of type: FROM MAC/IP TO MAC/IP PORT DROP
    if case == 7:
      self.rule_type = 7
      self.src = explode[0]
      self.dst = explode[3]
      self.protocol = None
      self.port1 = None   
      if isinstance(explode[4], int):
	self.port2 = explode[4]     
      else:
	print "7Rule not well-formed. Invalid port. Program terminated.\n"
	exit(1)	        
      
    #rule of type: FROM MAC/IP PORT TO MAC/IP PORT DROP
    if case == 8:
      self.rule_type = 7
      self.src = explode[0]
      self.dst = explode[4]
      self.protocol = None
      
      if filter(str.isdigit, explode[2]) != None:
	self.port1 = explode[2]     
      else:
	print "8Rule not well-formed. Invalid port. Program terminated.\n"
	exit(1)
	
      if filter(str.isdigit, explode[5]) != None:
	self.port2 = explode[5]     
      else:
	print "9Rule not well-formed. Invalid port. Program terminated.\n"
	exit(1)	         
   
   
  def to_s(self):
    return str(self.src) + " " + str(self.dst) + " " + str(self.port1) + " " + str(self.port2) + " " + str(self.rule_type) + " " + str(self.protocol)
    
  
  #method return 0 if no rule is matched, 1 otherwise (it actually means that packet must be dropped)
  def check_rule(self, packet):
    #possible payload
    #TODO not sure if ipv6 is available in current OpenFlow API
    ip4_payload = packet.find('ipv4')
    tcp_payload = packet.find('tcp')
    udp_payload = packet.find('udp')
    dhcp_payload = packet.find('dhcp')
    icmp_payload = packet.find('icmp')
    dns_payload = packet.find('dns')    
    lldp_payload = packet.find('lldp')    
        
    
    #packet must have same source address as this rule (MAC OR IP address)
    if self.rule_type == 1:
      if (str(self.src) == str(packet.src)):	
	return 1
      if (ip4_payload != None):
	if (str(ip4_payload.srcip) == str(self.src)):
	  return 1
      return 0
    
    #packet must have same source and destination addresses
    if self.rule_type == 2:
      if (self.src == packet.src and self.dst == packet.dst):
	return 1
      if (ip4_payload != None and ip4_payload.srcip == self.src and ip4_payload.dstip == self.dst):
	return 1
      return 0      
      
    #packet must have same source and travel on same protocol
    if self.rule_type == 3:
        
      if ((ip4_payload != None and ip4_payload.srcip == self.src)):
		
	
	if (self.protocol == "IP"):	  
	  return 1
	  
	if (self.protocol == "TCP" and tcp_payload != None):
	  return 1
	if (self.protocol == "UDP" and udp_payload != False):	  	  
	  return 1
	if (self.protocol == "DHCP" and dhcp_payload != None):	  
	  return 1
	if (self.protocol == "ICMP" and icmp_payload != None):		  
	  return 1
	if (self.protocol == "DNS" and dns_payload != None):		  
	  return 1
	if (self.protocol == "LLDP" and lldp_payload != None):	  
	  return 1
      return 0
      
      
    #packet must have same source and destination addresses and same protocol
    if self.rule_type == 4:
      if (((self.src == packet.src) and (ip4_payload != None and ip4_payload.srcip == self.src)) and ((self.dst == packet.dst) and (ip4_payload != None and ip4_payload.dstip == self.dst))):
	if (self.protocol == "IP" and ip4_payload != None):
	  return 1
	if (self.protocol == "TCP" and tcp_payload != None):
	  return 1
	if (self.protocol == "UDP" and udp_payload != None):
	  return 1
	if (self.protocol == "DHCP" and dhcp_payload != None):
	  return 1
	if (self.protocol == "ICMP" and icmp_payload != None):
	  return 1
	if (self.protocol == "DNS" and dns_payload != None):
	  return 1
	if (self.protocol == "LLDP" and lldp_payload != None):
	  return 1
      return 0
	  
    #packet must have same source+port of this rule
    if self.rule_type == 5:
      if ((self.src == packet.src) or (ip4_payload != None and ip4_payload.srcip == self.src)):
	if (ip4_payload != None and self.port1 == ip4_payload.srcport):
	  return 1
	if (tcp_payload != None and self.port1 == tcp_payload.srcport):
	  return 1
	if (udp_payload != None and self.port1 == udp_payload.srcport):
	  return 1
      return 0
      
    #packet must have same source address+port and same destination address (BUT NOT PORT)
    if self.rule_type == 6:
      if (((self.src == packet.src) or (ip4_payload != None and ip4_payload.srcip == self.src)) and ((self.dst == packet.dst) or (ip4_payload != None and ip4_payload.dstip == self.dst))):
	if (ip4_payload != None and self.port1 == ip4_payload.srcport):
	  return 1
	if (tcp_payload != None and self.port1 == tcp_payload.srcport):
	  return 1
	if (udp_payload != None and self.port1 == udp_payload.srcport):
	  return 1
      return 0
      
    #packet must have same source address (BUT NOT PORT) and same destination address + port 
    if self.rule_type == 7:
      if (((self.src == packet.src) or (ip4_payload != None and ip4_payload.srcip == self.src)) and ((self.dst == packet.dst) or (ip4_payload != None and ip4_payload.dstip == self.dst))):
	if (ip4_payload != None and self.port2 == ip4_payload.dstport):
	  return 1
	if (tcp_payload != None and self.port2 == tcp_payload.dstport):
	  return 1
	if (udp_payload != None and self.port2 == udp_payload.dstport):
	  return 1
      return 0   
      
    #packet must have same source address +port and same destination address + port      
    if self.rule_type == 8:      
      if (((self.src == packet.src) or (ip4_payload != None and ip4_payload.srcip == self.src)) and ((self.dst == packet.dst) or (ip4_payload != None and ip4_payload.dstip == self.dst))):
	if (ip4_payload != None and self.port1 == ip4_payload.srcport and self.port2 == ip4_payload.dstport):
	  return 1
	if (tcp_payload != None and self.port1 == tcp_payload.srcport and self.port2 == tcp_payload.dstport):
	  return 1
	if (udp_payload != None and self.port1 == udp_payload.srcport and self.port2 == udp_payload.dstport):
	  return 1
      return 0    
      
      
    return 0
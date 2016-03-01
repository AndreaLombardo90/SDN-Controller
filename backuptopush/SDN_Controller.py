from pox.core import core
from collections import defaultdict
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree
from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os
import re
from switch import Switch
from net_graph import NetGraph
import signal
from edge import Edge
from path import Path
from usersmanager import UsersManager
from rule import Rule
from timeit import default_timer as timer

log = core.getLogger()



class VideoSlice (EventMixin):

    def __init__(self):
	self.start_time = timer()
	self.begin_work = False
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)
	signal.signal(signal.SIGINT, self.signal_handler)          
	#list of Switch objects
	self.switches = []
	#graph used for path computation
	self.net_graph = NetGraph()
	self.policies = {}
        self.usrmgr = UsersManager()
	#loading user-classes policies
	self.loadpolicies()
	#loading users (TODO: new thread, managing new users communicated by another user manager server)
	self.loadUsers()
	#list of possible hosts (to be cleaned in order to avoid hosts/switch possible mix) linked to their switch
	#tuple in the form of (host_mac, switch_mac)
	self.possible_hosts = []
	#list of rules
	self.rules = []
	self.loadrules()
	#this configuration file follows that grammar: #MAC_ADDRESS1# #MAC_ADDRESS2# #BW#
	#bandwidth is expressed in Mbps
	self.loaded_net = False
	self.loaded_net = self.loadEdges()
	self.begin_work = True
  
    
    def loadEdges(self):
	#this method loads data belonging to edges in network that can be retrieved in bandwidths.conf
	cnt = 0
	edges_config = file("bandwidths.conf", "r")
	line = edges_config.readline().split()
	while len(line) != 0:
	  if (len(line) == 3):
	    self.net_graph.addEdge(line[0], line[1], int(line[2]))
	    cnt = cnt + 1
	  line = edges_config.readline().split()
	
	edges_config.close()
	
	if cnt != 0:
	  return True
	else:
	  return False
    
    def loadrules(self):
	rules_config = file("rules.conf", "r")
	line = rules_config.readline()
	while len(line) != 0:
	  r = Rule(line)
	  self.rules.append(r)
	  line = rules_config.readline()
	rules_config.close()
	
    def loadpolicies(self):
	#policies are specified in queues_policies.conf file according to the following grammar:
	#@class_name @bandwidth (bandwidth in Mbit)      
	queues_config = file("queues_policies.conf", "r")
	line = queues_config.readline().split()
	while len(line) != 0:
	  if (len(line) == 2):
	    if (type(line[0]) is str and line[1].isdigit()):
	      self.policies[line[0]] = line[1]        
	  line = queues_config.readline().split()
	
	queues_config.close()
	self.usrmgr.set_policies(self.policies)	
    
    def loadUsers(self):
        #users are specificed in users_classes.conf file along with classes they belong according to the following grammar:
        #@class_name
        #@user_ip
	users_file = file("users_classes.conf", "r")
	pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
	
	line = users_file.readline()
	actual_class = line
	
	
	while line != "":
	  if (pat.match(line)):
	    self.usrmgr.addUser(actual_class, line, "")
	  else:
	    self.usrmgr.addClass(line)
	    actual_class = line	    

	  line = users_file.readline()
	
	
	users_file.close()

    
    
    def _handle_LinkEvent (self, event):
	#event raised each time a link between two switches goes up or down in the net.
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)
	  
        if (event.added and self.loaded_net == False and self.begin_work == True):
	  self.net_graph.addEdge(sw1,sw2,1)
	  self.net_graph.addEdge(sw2,sw1,1)

	    
	    
	  

	
    def clean_hosts(self):
      #this method removes switches from possible hosts list
      to_be_removed = []
      
      for switch in self.switches:
	for host in self.possible_hosts:
	  if host[0] == switch.dpid:
	    to_be_removed.append(host)
      
      for h in to_be_removed:
	self.possible_hosts.remove(h)
      
    
    def printswitches(self):
      #debug method. it prints ARP table of each switch in the net
      output = file("rules.txt", "w")
      
      for r in self.rules:
	output.write(r.to_s())
	
      output.close()
    
    #every time a packet arrive to controller we'll update the graph according to the new
    #discovered hosts
    def update_graph(self):
      for host in self.possible_hosts:
	self.net_graph.addEdge(host[1], host[0], 0)
	self.net_graph.addEdge(host[0], host[1], 0)
    
    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """    
        packet = event.parsed
	self.printswitches()
	self.clean_hosts()
	self.update_graph()

	#packet filtering
	#check if this packet activates some rule
	check = False
	
	for r in self.rules:
	  if ((r.check_rule(event.parsed)) == 1):
	    #rule checked, must drop packet
	    check = True
	    break	 	
	
	
	def drop():
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    msg.data = event.ofp
	    msg.in_port = event.port
	    event.connection.send(msg)	    
	
        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)
            
            
            
            check = 0
            for i in self.possible_hosts:
	      if (i[0] == str(packet.src) or i[0] == str(packet.dst)):
		check = check + 1
	    
	    path = None
	    dictionary = None
            if (check == 2):
	      #Dijkstra is used only to compute paths between hosts, not for logistic informations between switches
	      (dist, prev, path, dictionary) = self.net_graph.Dijkstra(str(packet.src), str(packet.dst))

            
            
            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug("Got unicast packet for %s at %s (input port %d):",
                          packet.dst, dpid_to_str(event.dpid), event.port)

		
                try:
		  
		    #TODO:forwarding of packets according to source/destination user and his class
		    #using Dijkstra
		  
		    valid_path = True
		    
		    
		    if (path == None):
		      valid_path = False
		    else:
		      for i in path:
			if (i == None):
			  valid_path = False
			  break
			  
	            #resolve mapping between dictionary and path
	            if (valid_path == True):
		      for i in range(len(path)):
			path[i] = str(dictionary[path[i]])
		  

		    path_check = file("path_check.txt", "w")
		    path_check.write("loaded " + str(self.loaded_net) + " " + str(packet.src) + " " + str(packet.dst) + " " + str(path) + "\n")
		    path_check.close()
		    
		    if (check == 2 and valid_path == True and path.__contains__(str(this_dpid)) and (timer()-self.start_time) >= 20):
		      #if check equals 2 we need to check if Dijkstra returned a valid path for forwarding
		      #path decoding:
		      #1) find position in path of current switch (this_dpid)
		      #2) next hop will be in next position of path (if we are at the end of the path, then next hop will be packet.dst)
		      next_hop = None
		      for hop in path:
			if str(hop) == str(this_dpid):
			  if path.index(hop) == len(path)-1:
			    next_hop = str(packet.dst)
			    break
			  else:
			    next_hop = path[path.index(hop)+1]
			    break		  

	
		      for s in self.switches:
			if s.dpid == str(this_dpid):	

			  for k in s.ARPTable.keys():
			    if k == next_hop:
			      #entry available, we forward the packet on the correct port
			      msg = of.ofp_flow_mod()
			      #msg.idle_timeout = of.OFP_FLOW_PERMANENT
			      #msg.hard_timeout = of.OFP_FLOW_PERMANENT
			      msg.match = of.ofp_match.from_packet(packet, event.port)
			      for entry in s.ARPTable[k]:
				msg.actions.append(of.ofp_action_output(port = int(entry)))
				msg.data = event.ofp
				#msg.in_port = event.port
				event.connection.send(msg)
		       	
		      
		      
		    else:
		      forwarded = False
		      #source may be an host (MAC first time seen by switch)

		      found_host = False
		      for h_tuple in self.possible_hosts:
			if h_tuple[0] == str(packet.src):
			  found_host = True
		      if found_host == False:
			self.possible_hosts.append((str(packet.src), this_dpid))		    
		      
		      #forward the packet if the corresponding mapping (MAC -> output port) exists
		      for s in self.switches:
			if s.dpid == this_dpid:
			  stringa = str(packet.src)
  
			  if s.ARPTable.keys().__contains__(stringa) == False:
			    s.ARPTable[stringa] = []
			    s.ARPTable[stringa].append(event.port)				  
			  elif s.ARPTable.keys().__contains__(stringa) == True and s.ARPTable[stringa].__contains__(event.port) == False:
			    s.ARPTable[stringa].append(event.port)
			  
			  for k in s.ARPTable.keys():
			    if k == packet.dst:
			      #entry available, we forward the packet on the correct port
			      msg = of.ofp_flow_mod()
			      #msg.idle_timeout = of.OFP_FLOW_PERMANENT
			      #msg.hard_timeout = of.OFP_FLOW_PERMANENT
			      msg.match = of.ofp_match.from_packet(packet, event.port)
			      for entry in s.ARPTable[k]:
				msg.actions.append(of.ofp_action_output(port = int(entry)))
				msg.data = event.ofp
				#msg.in_port = event.port
				event.connection.send(msg)
			      forwarded = True		    
			    
		      
		      if forwarded == False:
			#Switch doesn't know where to forward the packet, so it will be flooded on each available port.
			msg = of.ofp_flow_mod()
			#msg.idle_timeout = of.OFP_FLOW_PERMANENT
			#msg.hard_timeout = of.OFP_FLOW_PERMANENT
			msg.match = of.ofp_match.from_packet(packet, event.port)
			msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
			msg.data = event.ofp
			msg.in_port = event.port
			event.connection.send(msg)		      
		      
		      #1) Get incoming packet
		      #2) Check if there is the corresponding entry for forwarding that packet in (MAC) -> input port map
		      #3) If it's this the case, switch will forward on that port
		      #4) Otherwise, packet will be flooded on each available port
		      #5) Nonetheless we store the information saying that packets incoming from srcMAC belong to the input port
		      #6) dstMAC must be on one of the other ports; we'll surely discover it soon


                except AttributeError:
                    log.debug("packet type has no transport ports, flooding")

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        if check == False:
	  forward()
	else:
	  drop()


    def _handle_ConnectionUp(self, event):
        #event raised each time a new switch goes up
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)
	
	#check if this switch is already known to the controller
	check = False
	
	for i in self.switches:
	  if (i.dpid == dpid):
	    check = True
	
	if check == False:
	  s = Switch(dpid)
	  self.switches.append(s)
	  for port in event.ofp.ports:
	    s.addPort(port.name, port.port_no, port.hw_addr)
	
	
	for s in self.switches:
	  for port in s.ports:
	    #insert all queues-policies for every port of this switch  
	    
	    #building the corresponding ovs-vsctl command
	    if (not not self.policies.keys()):
	      command = "ovs-vsctl set port " + port.ifname + " qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0"
	      queue_index = 1
	      for key in self.policies.keys():
		command = command + "," + str(queue_index) + "=@q" + str(queue_index) 
		queue_index = queue_index + 1
		if queue_index == len(self.policies.keys()):
		  break	      
	      command = command + " -- "
	      
	      queue_index = 0
	      for key in self.policies.keys():
		command = command + "--id=@q" + str(queue_index) + " create queue other-config:min-rate=" + str(self.policies[key]) + " other-config:max-rate=" + str(self.policies[key]) + " -- "
		queue_index = queue_index + 1
		if queue_index == len(self.policies.keys()):
		  break
	      os.system(command)
	    

	
	  
	  
	  
    def signal_handler(self, signal, frame):
	self.printswitches()
	self.net_graph.printGraph()
	exit(0)
	  

	  
	  
def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the SDN Controller module
    '''
    core.registerNew(VideoSlice)

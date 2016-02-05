import time
import datetime

class NetGraph:
  def __init__(self):
    #each key of this dictionary is a vertex of the graph
    #values are tuples (destination_vector, weight) representing edges
    self.nodes = {}
  
  
  #this method add and edge from node1 to node2 with weight "weight"
  def addEdge(self, node1, node2, weight):
    found = False
    
    if (self.nodes.keys().__contains__(node1) == False):
      self.nodes[node1] = []
      self.nodes[node1].append((node2, weight))
    else:
      for c in self.nodes[node1]:
	if (c[0] == node2):
	  found = True
      if found == False:
	self.nodes[node1].append((node2, weight))
	
    found = False	
    if (self.nodes.keys().__contains__(node2) == False):
      self.nodes[node2] = []
      self.nodes[node2].append((node1, weight))
    else:
      for c in self.nodes[node2]:
	if (c[0] == node1):
	  found = True
      if found == False:
	self.nodes[node2].append((node1, weight)) 	
      
  
  #this method remove the edge which links node1 to node2, if it exists
  def removeEdge(self, node1, node2):
    candidates = []
    if (self.nodes.keys().__contains__(str(node1)) == True):
      for nod_tuple in self.nodes[str(node1)]:
	if nod_tuple[0] == node2:
	  candidates.append(nod_tuple)
	
    for tup in candidates:
      self.nodes[str(node1)].remove(tup)
    
    
  #debug method for printing the graph structure in a text file
  def printGraph(self):
    output = file("graph.txt","w")
    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    output.write("\n\nTIMESTAMP INIT: " + str(st) + "\n\n")
    
    for key in self.nodes.keys():
      output.write("Nodo " + str(key) + ":\n")
      for value in self.nodes[key]:
	output.write(str(value) + " -> ")
      output.write("\n")

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')      
    output.write("TIMESTAMP END: " + str(st) + "\n\n\n")
    
    output.close()


  #this method take src and dst as MAC address then map them to integer identifiers (more comfortable to be managed)
  def Dijkstra(self, src, dst):
    dictionary = {}
    index = 0
    dist = []
    prev = []
    path = []
    
    if (self.nodes.keys().__contains__(str(src)) == False or self.nodes.keys().__contains__(str(dst)) == False):
      return ([],[],[])
    
    for key in self.nodes.keys():
      dictionary[index] = key
      index = index + 1
    
    def get_index(vertex):
      for k in dictionary.keys():
	if (str(dictionary[k]) == vertex):
	  return k 
	  
	  
    try:     
      (dist, prev) = self.wrapper_Dijkstra(dictionary, get_index(str(src)), get_index(str(dst)))
    except KeyError:
      print("errorwrapper") 
    
    path = self.rebuild_path(prev, get_index(str(dst)))
  
    
    return (dist, prev, path, dictionary)
    
    

  #real Dijkstra implementation for the Dijkstra interface
  def wrapper_Dijkstra(self, dictionary, src, dst):
    
    def get_index(vertex):
      for k in dictionary.keys():
	if (str(dictionary[k]) == str(vertex)):
	  return k
    
    
    dist = [0 for i in range(0,len(self.nodes.keys()))]
    prev = [0 for i in range(0,len(self.nodes.keys()))]
    dist[src] = 0
    prev[src] = None   
    
    Q = self.nodes.keys()
    
    if len(Q) < 2:
      return ([],[])
    

    for v in dictionary.keys():
      if v != src:
	dist[v] = float('inf')
	prev[v] = None

    while len(Q) > 0:
      minimum = float('inf')
      u = None
      to_remove = None
      for n in Q:
	if dist[get_index(str(n))] < minimum:
	  minimum = dist[get_index(str(n))]
	  u = get_index(str(n))
	  to_remove = n
      Q.remove(to_remove)
   

      for v in self.nodes[dictionary[u]]:
	alt = min(dist[u] + v[1], v[1])#dist[u] + v[1]#min(dist[u], v[1])
	if alt < dist[get_index(str(v[0]))]:
	  dist[get_index(str(v[0]))] = alt
	  prev[get_index(str(v[0]))] = u
	      
    return (dist, prev)
  
  #this method rebuild a path calculated by Dijkstra method starting for prev vector
  def rebuild_path(self, prev, target):
    S = []
    u = target
    while prev[u] != None:
      S.append(u)
      u = prev[u]
    return S
  
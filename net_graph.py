import time
import datetime

class NetGraph:
  def __init__(self):
    #each key of this dictionary is a vertex of the graph
    #values are tuples (destination_vector, weight) representing edges
    self.nodes = {}
  
  
  #this method add and edge from node1 to node2 with weight "weight"
  def addEdge(self, node1, node2, weight):
    if (self.nodes.keys().__contains__(node1) == False):
      self.nodes[node1] = []
      self.nodes[node1].append((node2, weight))
    elif (self.nodes[node1].__contains__((node2, weight)) == False):
      self.nodes[node1].append((node2,weight))    
      
  
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
    for key in self.nodes.keys():
      dictionary[key] = index
      index = index + 1
      
    (dist, prev) = self.wrapper_Dijkstra(dictionary[src], dictionary[dst])
    path = self.rebuild_path(prev, dictionary[dst])
    
    
    
  
  #real Dijkstra implementation for the Dijkstra interface
  def wrapper_Dijkstra(self, src, dst):
    dist = [0 for i in range(0,len(self.nodes.keys()))]
    prev = [0 for i in range(0,len(self.nodes.keys()))]
    dist[src] = 0
    prev[src] = None
    
    Q = self.nodes.keys()
    
    for v in self.nodes.keys():
      if v != src:
	dist[v] = float('inf')
	prev[v] = None

    while len(Q) > 0:
      minimum = int('inf')
      u = None
      for n in Q:
	if dist[n] < minimum:
	  minimum = dist[n]
	  u = n
      Q.remove(u)
      
      for v in self.nodes[u]:
	alt = dist[u] + v[1]
	if alt < dist[v[0]]:
	  dist[v[0]] = alt
	  prev[v[0]] = u
	  
    return (dist, prev)
  
  #this method rebuild a path calculated by Dijkstra method starting for prev vector
  def rebuild_path(self, prev, target):
    S = []
    u = target
    while prev[u] != None:
      S.append(u)
      u = prev[u]
    return S
  
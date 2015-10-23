from edge import Edge

class Path:
  def __init__(self, h1, h2):
    #source node
    self.h1 = h1
    #sink node
    self.h2 = h2
    #vertices list for this path
    self.path = []
    #minimum guaranted bandwidth
    self.min_bw = 0
  
  #add node to current path
  def addEdge(self, node):
    self.path.append(node)
    
    tmp_max = 99999
    
    for edge in self.path:
      if edge.bw < tmp_max:
	tmp_max = edge.bw
	
    self.min_bw = tmp_max
    
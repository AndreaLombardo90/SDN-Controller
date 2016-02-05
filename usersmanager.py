from user import User

class UsersManager:
  def __init__(self):
    #dictionary of classes (keys) related to user lists (values) for each one
    self.classes = {}
    #dictionary of polcies. Each key identifies a user-class name and each value the minimum bandwidth guaranted for that class
    self.policies = {}
  
  #add user with his ip and his mac to the userclass uclass
  def addUser(self, uclass, ip, mac):
    u = User(uclass, ip, mac)
    
    if self.classes.keys().__contains__(uclass) == False:
      self.classes[uclass] = []
      self.classes[uclass].append(u)
    else:
      self.classes[uclass].append(u)

  #add userclass uclass to classes
  def addClass(self, uclass):
    if self.classes.keys().__contains__(uclass) == False:
      self.classes[uclass] = []
  
  #set current list of policies to those specified in policies vector.
  def set_policies(self, policies):
    self.policies = policies
    
  def print_users(self):
    s = ""
    
    s = s + "Classes:\n"
    for key in self.classes.keys():
      s = s + key + "\n"
    
    s = s + "Users: \n"
    
    for key in self.classes.keys():
      s = s + key + ":\n" 
      for usr in self.classes[key]:
	s = s  + usr.ip + " " + "\n"
      
    return s
    
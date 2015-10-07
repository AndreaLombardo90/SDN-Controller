class User:
  def __init__(self, uclass, ip, mac):
    #class for this user (e.g. "Free", "Premium" or "Ultra")
    self.uclass = uclass
    #MAC address of user's machine
    self.mac = mac
    #IP address of user's machine
    self.ip = ip
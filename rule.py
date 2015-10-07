class Rule:
  '''
  Rule can be of three types:
  
  drop every packet coming from X_MAC/IP independently by his content:
  
  X_MAC/IP DROP
  
  drop every packet that has X_MAC/IP as source and Y_MAC/IP as destination independently by his content:
  
  FROM X_MAC/IP TO Y_MAC/IP DROP
  
  drop every packet originated  by X_MAC/IP with Y_MAC/IP as destination traveling on PROTOCOL:
  
  IF PROTOCOL FROM X_MAC/IP TO Y_MAC/IP
  
  '''
  def __init__(self, rule_str):
    '''
    before we can instatiate the new rule, we must be sure that it respect one of the forms listed above

    case will be 0 if no valid rule can be extracted by rule_str, others values are:
    
    1 -> X_MAC/IP DROP
    
    2 -> FROM X_MAC/IP TO Y_MAC/IP DROP
    
    3 -> IF PROTOCOL FROM X_MAC/IP TO Y_MAC/IP
    
    '''
    
    case = 0
    
    #X_MAC/IP DROP
    explode = rule_str.split()
    pat_ip = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    pat_mac = re.compile(r'^([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})\:([0-9A-F]{1,2})$', re.IGNORECASE)
    
    if ()
    
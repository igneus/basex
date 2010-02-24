#
# [AW] Description for Session and Client class, incl. example(s)
#
# (C) Workgroup DBIS, University of Konstanz 2005-10, ISC License
 
import hashlib, socket, array, getopt, sys, getpass
 
class Session():
  
  # Initializes the session.
  def __init__(self, host, port, user, pw):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # allocate 4kb buffer
    self.__buf = array.array('B', '\0' * 0x1000)
    self.__init()

    # receive timestamp
    ts = self.__readString()

    pwmd5 = hashlib.md5(pw).hexdigest()
    m = hashlib.md5()
    m.update(pwmd5)
    m.update(ts)
    complete = m.hexdigest()
    
    # send user name and hashed password/timestamp
    s.send(user)
    s.send('\0')
    s.send(complete)
    s.send('\0')
    
    # receives success flag
    if s.recv(1) != '\0':
      raise IOError("Access Denied.")
  
  # Executes a command.
  def execute(self, com, out):
    s.send(com)
    s.send('\0')

    self.__init()
    out.write(self.__readString())
    self.__info = self.__readString()
    return self.__read() == 0

  # Returns the info string.
  def info(self):
    return self.__info
  
  # Closes the socket.
  def close(self):
    s.send('exit')
    s.close()
   
  # Initializes the byte transfer
  def __init(self):
    self.__bpos = 0
    self.__bsize = 0
         
  # Receives a string from the socket.
  def __readString(self):
    bf = array.array('B')
    while True:
      b = self.__read()
      if b:
        bf.append(b)
      else:
        return bf.tostring()
         
  # Returns the next byte
  def __read(self):
    # Cache next bytes
    if self.__bpos == self.__bsize:
      self.__bsize = s.recv_into(self.__buf)
      self.__bpos = 0

    # Return current byte
    b = self.__buf[self.__bpos]
    self.__bpos += 1
    return b

# This class offers an interactive BaseX console
class Client(object):
  # Initializes the client.
  def __init__(self, host, port):
    self.__host = host
    self.__port = port
    print 'BaseX Client'
    print 'Try "help" to get some information.'       

  # Creates a session.   
  def session(self):
    user = raw_input('Username: ');
    pw = getpass.getpass('Password: ');
    try:
      global session
      session = Session(self.__host, self.__port, user, pw)
      self.__console()
      session.close()
      print "See you."
    except IOError as e:
      print e
  
  # Runs the console.
  def __console(self):
    out = sys.stdout
    session.execute("SET INFO ON", out)
    while True:
      com = str(raw_input('> ')).strip()
      if com == 'exit':
        break 
      if com:
        session.execute(com, out)
        print session.info()

# Reads arguments -p and -h.
def opts():
    try:
      opts, args = getopt.getopt(sys.argv[1:], "-p:-h", ["port", "host"])
    except getopt.GetoptError, err:
      print str(err)
      sys.exit()
    global host
    global port
    host = "localhost"
    port = 1984
    
    for o, a in opts:
      if o == "-p":
        port = int(a)
      if o == "-h":
        host = a

# Main method.
if __name__ == '__main__':
  opts()
  Client(host, port).session()

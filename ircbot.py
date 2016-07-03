import socket
import cevents
import json
import signal
import sys
import os

class IRCBot: #Main bot class

 def __init__(self):
  self.config = json.load(open("conf.json", "r"))
  self.config = self.config['ircbot']
  self.isquitting = False
  self.parseline = ""
  if self.config['ipv6'] == True:
   self.ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  else:
   self.ircsock = socket.socket(socket.SOCK_STREAM)
   
 def connect(self):
  self.ircsock.connect((self.config['server'], self.config['port']))
  self.handle = self.ircsock.makefile(mode='rw', buffering=1, encoding='utf-8', newline='\r\n')
  print("NICK", self.config['nick'], file=self.handle)
  print("USER", self.config['ident'], "localhost", "localhost", ':'+self.config['realname'], file=self.handle)
  self.mainloop()

 def mainloop(self):
  for line in self.handle:
   line = line.strip()
   self.parseline = line.strip()
   if self.config['debugmode'] == True: #Suppresses most server messages if false
    print(line)
   if line.split()[1] == "001":
    print("Connection successful")
    print("JOIN "+self.config['channels'], file=self.handle)
   elif line.split()[0] == "PING": #Reply to PINGs
    print("PONG :"+line.split(':')[1], file=self.handle)
    
   elif line.split()[0] == "ERROR": #If the server disconnects us
    if self.isquitting == False:
     print("Disconnected")
     self.restart()
    
##########################
#Event capturing
########################## 
   elif line.split()[1] == "PRIVMSG":
    print(line)
    cevents.commandevent(self, self.config['nick'], line)  
    
    
#########################
#Main IRC functions
#########################


 def msg(self, target, message):
  print("PRIVMSG --> {t}: {m}".format(t=target,m=message))
  print("PRIVMSG "+target+" :"+message, file=self.handle)
  
 def act(self, target, message):
  print("ACTION --> {t}: {m}".format(t=target,m=message))
  print("PRIVMSG "+target+" :\001ACTION "+message+"\001", file=self.handle)
  
  
 def notice(self, target, message):
  print("NOTICE "+target+" :"+message, file=self.handle)
  
 def join(self, channel):
  print("JOIN "+channel, file=self.handle)
  
 def part(self, channel, message):
  if message == None:
   print("PART "+channel, file=self.handle)
  else:
   print("PART "+channel+" :"+message, file=self.handle)
  
 def quit(self, message, restart):
  if restart == True:
   self.isquitting = False
  else:
   self.isquitting = True
  if message == None:
   print("QUIT", file=self.handle)
  else:
   print("QUIT :"+message, file=self.handle)
   
 def kick(self, channel, user, message):
  if message == None:
   print("KICK "+channel+" "+user, file=self.handle)
  else:
   print("KICK "+channel+" "+user+" :"+message, file=self.handle)
   
 def getnames(self, channel):
  print("NAMES "+channel, file=self.handle)
  if self.parseline.split()[1] == "353":
   names = self.parseline.split()[5]
   return names
   
 def restart(self):
  py = sys.executable
  print("Restarting...")
  os.execl(py, py, * sys.argv)
  

import re
import json
import lxml.html
import requests
from PIL import Image
from mod import *
import random
import traceback

conf = json.load(open("conf.json", "r"))
conf = conf['cevents']
roulette_chamber = 6

def urlparse(url):    #URL parsing for title. Needs lxml
     h = requests.head(url) #Send a HEAD request first for meta-info such as content type and content length without requesting the entire content
     content_type = h.headers['Content-Type']
     if h.status_code != 200:
      return "Err: "+str(h.status_code)
     else:
      if re.match("(image\S+?(?P<format>(jpeg)|(png)|(gif)))", content_type):
       print("Image URL")
       imgpattern = "(image\S+?(?P<format>(jpeg)|(png)|(gif)))"
       if int(h.headers["content-length"]) > 4194304: #Ignore if bigger than 4 MiB
        print("Ignored large image")
        pass
       else:
        reg = re.compile(imgpattern)
        imgformat = reg.search(content_type)
        f = requests.get(url, stream=True)
        s = Image.open(f.raw)
        msg = "{f} image, {size}, {w} x {h}".format(f=imgformat.group("format").upper(),size=readablesize(int(f.headers["content-length"])),w=s.size[0],h=s.size[1])
        return msg
      else:
       f = requests.get(url)
       s = lxml.html.fromstring(f.content) #lxml wants a consistently undecoded file, so f.content does it
       title = '[ '+s.find(".//title").text+' ]'
       title = title.replace('\n', ' ')
       return title

def readablesize(i):
 if i >= 1048576:
  size = float(i / 1048576)
  return "{s} MiB".format(s=str("%.2f" % size))
 elif i >= 1024:
  size = float(i / 1024)
  return "{s} KiB".format(s=str("%.2f" % size))
 else:
  return "{s} Bytes".format(s=str(i))
  
def blist(user):					
	bestand = open('blacklist.txt', 'r')
	for line in bestand:
		if user in line:
			rstatus = True
			return rstatus
		else:
			rstatus = False
			return rstatus

  

def commandevent(botcontext, curnick, data): #Main command event for PRIVMSG events
 bl_pass = False
 global roulette_chamber
 
##################
#Regex matching
##################

 if re.match("(:(?P<nick>\S+)!(?P<hostmask>\S+) (?P<event>\S+) (?P<target>\S+) :(?P<message>.+))", data): #Event with message
  cmdreg = re.compile("(:(?P<nick>\S+)!(?P<hostmask>\S+) (?P<event>\S+) (?P<target>\S+) :(?P<message>.+))")
  parseddata = cmdreg.search(data)
 urlreg = re.compile("(https?://\S+)")
 url = urlreg.search(parseddata.group("message"))
 target = parseddata.group("target")
 msgnick = parseddata.group("nick")
 message = parseddata.group("message")
 
 rstatus = blist(msgnick) #Checks if a user is whitelisted
 if rstatus == True:
  print("User in blacklist, passing")
  bl_pass = True
 else:
  bl_pass = False
  

 try:
  if bl_pass != True:
  
   if message[0] == "$":
    cmddata = message[1:].split(" ", 1)
    if len(cmddata) > 1:
     cmd, args = cmddata[0], cmddata[1]
    else:
     cmd, args = cmddata[0], None

############################
#Start of commands
############################
    if cmd == "ping":
     botcontext.msg(target, "Pong!")
    elif cmd == "timertest":
     if args == None:
      botcontext.notice(msgnick, "No argument supplied")
     else:
      botcontext.msg(target, "Timer started for {s} seconds for {n}".format(s=args,n=msgnick))
  
    elif cmd == "reverse":
     rev = str(args[::-1])
     botcontext.msg(target, rev)
   
    elif cmd == "say":
     botcontext.msg(target, args)
    
    elif cmd == "act":
     botcontext.act(target, args)
    
    elif cmd == "eval":
     if msgnick in conf['admins']:
      try:
       botcontext.msg(target, eval(args))
      except Exception as e:
       botcontext.msg(target, "Err: "+str(e))
     else:
      botcontext.notice(msgnick, "Permission denied")
      
    elif cmd == "hug":
     botcontext.act(target, "hugs "+msgnick)
     
    elif cmd == "roulette":
     trig = random.randint(1, roulette_chamber)
     if trig == roulette_chamber:
      roulette_chamber = 6
      botcontext.msg(target, "*BANG*")
      botcontext.kick(target, msgnick, "Lost at roulette")
     else:
      roulette_chamber -= 1
      botcontext.msg(target, "*click*")
      
      
    elif cmd == "restart":
     if msgnick in conf['admins']:
      botcontext.quit("Restarting", True)
     else:
      botcontext.notice(msgnick, "Permission denied")
      

    
############################
#Start of raw commands
############################
    
   if message.startswith("ayy"):
    botcontext.msg(target, "lmao")   
   elif url: #URL parsing
    if msgnick == curnick:
     print("Own url, passing")
    else:
     if re.match("(https?://(www.)?((derpibooru[.]org)|(derpiboo[.]ru))\S+)", url.group(0)): #Deripbooru URLs
      reg = re.compile("(https?://(www.)?((derpibooru[.]org)|(derpiboo[.]ru))(/images/)?/?(?P<id>[0-9]*))")
      num = reg.search(url.group(0))
      statstr = derpi.stats_string(num.group("id"))
      if statstr == None:
       botcontext.msg(target, "Nothing")
      else:
       botcontext.msg(target, statstr[0])
       botcontext.msg(target, statstr[1])
     else:
      title = urlparse(url.group(0))
      if title == None:
       pass
      else:
       botcontext.msg(target, title)
   
 except Exception as e:
  print(traceback.format_exc())

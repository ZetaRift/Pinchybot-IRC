import re
import json
import lxml.html
import requests
from PIL import Image
from mod import *
import random
import traceback
import cmds
import importlib

conf = json.load(open("conf.json", "r"))
conf = conf['cevents']
roulette_chamber = 6
cm = cmds.Commands()

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

def parsemessage(m):
	c = ''
	for i in m:
		c+=i+" "
	c = c.strip(":")
	c = c.strip()
	return c
	
def reloadmod():
	global cm
	try:
		importlib.reload(cmds)
		cm = cmds.Commands()
		return 0
	except:
		return str(traceback.format_exc())

def commandevent(botcontext, curnick, data): #Main command event for PRIVMSG events
	bl_pass = False
 
##################
#Regex matching
##################

# if re.match("(:(?P<nick>\S+)!(?P<hostmask>\S+) (?P<event>\S+) (?P<target>\S+) :(?P<message>.+))", data): #Event with message
#  cmdreg = re.compile("(:(?P<nick>\S+)!(?P<hostmask>\S+) (?P<event>\S+) (?P<target>\S+) :(?P<message>.+))")
#  parseddata = cmdreg.search(data)
	user = data.split()[0]
	msgnick = user.rsplit("!", 1)
	msgnick = msgnick[0].strip(":")
	target = data.split()[2]
	message = parsemessage(data.split()[3:])
	urlreg = re.compile("(https?://\S+)")
	url = urlreg.search(message)
	if url:
		print(url.group(0))
 
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
				
				
				if cmd == "eval":
					if msgnick in conf['admins']:
						try:
							botcontext.msg(target, eval(args))
						except Exception as e:
							botcontext.msg(target, "Err: "+str(e))
					else:
						botcontext.notice(msgnick, "Permission denied")
				elif cmd == "restart":
					if msgnick in conf['admins']:
						botcontext.quit("Restarting", True)
					else:
						botcontext.notice(msgnick, "Permission denied")
      
				elif cmd == "nick":
					if msgnick in conf['admins']:
						botcontext.nick(args)
					else:
						botcontext.notice(msgnick, "Permission denied")

				elif cmd == "csay":
					if msgnick in conf['admins']:
						params = args[0:].split(" ", 1)
						botcontext.msg(params[0], params[1])
					else:
						botcontext.notice(msgnick, "Permission denied")
				elif cmd == "reloadmod":
					if msgnick in conf['admins']:
						s = reloadmod()
						if s == 0:
							botcontext.msg(target, "Successfully reloaded commands module")
						else:
							botcontext.msg(target, "Reloading failed")
							print(s)
				else:
					if hasattr(cm, cmd):
						if cmd.isalnum() == True:
							try:
								cmdcall = getattr(cm, cmd)
								cmdcall(botcontext, target, msgnick, args)
							except:
								print("Something borked")

 
    
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

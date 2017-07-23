 


class Roulette:
	def __init__(self):
		self.chamber = 6
  
	def reset(self):
		self.chamber = 6
  
	def fire(self):
		trig = random.randint(1, self.chamber)
		if trig == self.chamber: #Bullet chamber
			self.chamber = 6
			return True
		else:
			self.chamber -= 1
			return False
roulette = Roulette()

def binconv(arg):
	if len(arg) > 64:
		return "Too long"
	else:
		if str(arg).isdigit():
			return "{N}".format(N=bin(int(arg)).replace("0b", "", 1))
		else:
			c = ''
			for s in arg:
				c+=''.join(str(ord(s) >> i & 1) for i in range(8)[::-1]) + " "
			return c


class Commands:
	def __init__(self): #Placeholder, for now
		self.a = None
		
	def ping(self, client, target, msgnick, args):
		client.msg(target, "Pong!")

	def timertest(self, client, target, msgnick, args):
		if args == None:
			client.notice(msgnick, "No argument supplied")
		else:
			client.msg(target, "Timer started for {s} seconds for {n}".format(s=args,n=msgnick))
			
	def reverse(self, client, target, msgnick, args):
		rev = str(args[::-1])
		client.msg(target, rev)
		
	def say(self, client, target, msgnick, args):
		client.msg(target, args)
	
	def act(self, client, target, msgnick, args):
		client.act(target, args)
		
	def binary(self, client, target, msgnick, args):
		if args == None or args.isspace():
			client.notice(msgnick, "No argument supplied")
		else:
			client.msg(target, binconv(args))
	def roulette(self, client, target, msgnick, args):
		if roulette.fire() == True:
			client.msg(target, "*BANG*")
			client.kick(target, msgnick, "Lost at roulette")
		else:
			client.msg(target, "*click*")

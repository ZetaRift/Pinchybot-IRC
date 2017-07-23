#!/usr/bin/python3.4

import os
import sys
import traceback


def pyvercheck():
	if sys.version_info < (3, 0):
		print("Requires python 3.x, exiting.")
		sys.exit(1)

def run():
	pyvercheck()
	print("Child PID: "+str(os.getpid()))
	try:
		import ircbot
	except ImportError:
		print(traceback.format_exc())
		print("Cannot find ircbot module, exiting")
		sys.exit(1)
	bot = ircbot.IRCBot()
	bot.connect()





if __name__ == "__main__":
	print("Master PID:"+str(os.getpid()))
	do_fork = True
	while do_fork:
		cpid = os.fork()
		if cpid == 0:
			run()
		pid, status = os.waitpid(cpid, 0)
		if status == 1280 or 256:
			print("Restarting child process..")
		print(status)
		do_fork = (status == 1280 or status == 256)

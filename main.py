#!/usr/bin/python3.4

import os
import sys


def pyvercheck():
 if sys.version_info < (3, 0):
  print("Requires python 3.x, exiting.")
  sys.exit(1)

def run():
 pyvercheck()
 try:
  import ircbot
 except ImportError:
  print("Cannot find ircbot module, exiting")
  sys.exit(1)
 bot = ircbot.IRCBot()
 bot.connect()





if __name__ == "__main__":
 run()
#!/usr/bin/env python2.7

###	Import
import os, sys
import SocketServer as ss
import json as j
import socket as s
import urllib2

### Define
def path():
	###	returns current directory above in string format
	dirUp = os.path.dirname(os.path.realpath(sys.argv[0])).split("/")
	dirUp_ = ""
	for n in range(1,len(dirUp)-1) :
		dirUp_ = dirUp_ + "/" + dirUp[n]
	return dirUp_

###	Operate
class Server(ss.ThreadingTCPServer):
	allow_reuse_address = True

class Handler(ss.BaseRequestHandler):
	def handle(self):
		data_j = open("%s/log_input/stream_log.json"%(path()),"r",3333333)
		data_s = data_j.read()
		self.request.sendall(data_s)

stream = Server(('127.0.0.1', 50009),Handler)
stream.serve_forever()

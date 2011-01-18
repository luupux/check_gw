#!/usr/bin/python -t
from optparse import OptionParser
import os
import subprocess
import re
import time
import string
import sys
__author__="Mauro Ferrigno mauro@flink.it"

verbose=None
#listhost=['151.1.1.1','www.google.it','193.43.2.1','222.222.222.221','111.222.222.221']
listhost=['222.222.222.221','111.222.222.221']
listgw=['10.0.1.250','10.0.1.254']

class ping:
	def __init__(self,lifeline="NONE",report="NONE",verbose=None):	
		self.lifeline = re.compile(r"(\d) received")
		self.report = ("No response","Partial Response","Alive")
		self.countok=[]
		self.verbose=verbose

	def pinghost(self,listhost):
		''' RITORNA L' IP DEGLI HOST RAGGIUNGIBILE'''
		self.listhost=listhost
		for host in self.listhost:
			ip = str(host)
			pingaling = os.popen("ping -w2 -q -c2 "+ip,"r")
			if self.verbose :
				print "Testing ",ip,
				sys.stdout.flush()
			while 1:
				line = pingaling.readline()
				if not line: break
				igot = re.findall(self.lifeline,line)
				if igot:
					if self.verbose :
						print self.report[int(igot[0])]
					if int(igot[0]) == 2:
						self.countok.append(host)
		return self.countok

	def calcavaibility(self,al,warn,crit,verbose="NONE"):
		"""CALCOLA LA PERCENTUALE PER LE SOGLIE WARN E CRIT"""
		self.al = al
		self.crit = crit
		self.warn = warn
		pingok = float(len(self.al))
		ghost = float(len(self.listhost))
		result = '%.0f' %(round((pingok/ghost) *100))
		if self.verbose :
			print "WARN "+str(warn)
			print "CRIT "+str(crit)
			print "RESULT "+result

		if int(result) < int(crit):
			return " CRITICAL "+result+"% PACKET RECEIVED"

		if int(result) < int(warn):
			return " WARNING "+result+"% PACKET RECEIVED"

		return " OK "+result+"% PACKET RECEIVED"
################# END  CLASS PING ########

def statuscode(checkval):
	if re.match(r'^.*OK',checkval,re.IGNORECASE):
		return 0
	elif re.match(r'^.*WARNING',checkval,re.IGNORECASE):
		return 1
	elif re.match(r'^.*CRITICAL',checkval,re.IGNORECASE):
		return 2
	else:
		return 3
################ END FUNCTION STATUSCODDE  ##############

class parseinput:
	def __init__(self,options=None,args=None):
		parser = OptionParser()
		parser.add_option("--warn",dest="warn",default="None",help="Warning  threshold")
		parser.add_option("--crit",dest="crit",default="None",help="Critical threshold")
		parser.add_option("--verb",action="store_true", dest="verb",help="Verbose ping")
		(options, args) = parser.parse_args()
		self.options=options
		self.args=args
		options.fargs=' '.join(args)
		self.fargs = options.fargs

		if len(sys.argv)==1:
			parser.error("-h for help")
		
		if options.warn == "None":
			parser.error("options --wan not found")

		if options.crit == "None":
			parser.error("options --crit not found")
################ END CLASS PARSEINPUT ##############

class managegw:
	def __init__(self,listgw,verbose=None):
		self.verbose=verbose
		self.listgw=listgw
		self.al=[]
		for elem in os.popen("route -n").read().split("\n"):
			if re.match("^[0-9]", elem.strip()):
				self.al.append(elem)
		self.activegw = self.al[-1].split()[1]
		self.othergw = filter(lambda x:  x!=self.activegw,listgw)

	def getactivegw(self):
		return 	self.activegw


	def getothergw(self):
		return str(self.othergw[0])

	def setroutegw(self):
		ip=self.getothergw()
		#self.cmdline='route add default gw '+ip
		self.cmdline='route add -host 217.133.71.30  gw '+ip
		p=subprocess.Popen(self.cmdline, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		stdout, stderr = p.communicate()
#		stdin,stdout,stderr = os.popen3('route add default gw '+ip,'r')
		self.verbose="PIPPO"
		if stderr:
			if self.verbose :
				print stderr
			return 1
		
		if not stdout: 
			if self.verbose :
				print "Add new gateway ",ip,
				sys.stdout.flush()
			return 0
		else:
			if self.verbose :
				print line
			return 1

#activegw =  managegw(listgw).getactivegw()
#print "ACTIVEGW "+str(activegw)
newgw = managegw(listgw).setroutegw()
#newgw = managegw(listgw).getothergw()
#print "NEWGW "+str(newgw)
sys.exit(0) 
################ END CLASS managegw ##############
def main():
	pi = parseinput()
	verbmode = pi.options.verb
	a = ping(verbose=verbmode)
	pingresults = a.pinghost(listhost)
	resultcode = a.calcavaibility(pingresults,pi.options.warn,pi.options.crit)
	gw = ping().pinghost(['151.1.1.3'])
	print gw
	print resultcode
	sys.exit(statuscode(resultcode))

		

	

if __name__=="__main__":
	main()


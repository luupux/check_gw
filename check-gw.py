#!/usr/bin/python -t
from optparse import OptionParser
import os
import subprocess
import re
import time
import string
import sys
__author__="Mauro Ferrigno mauro@flink.it"

#verbose=True
#listhost=['151.1.1.1','www.google.it','193.43.2.1','dns.nic.it','151.1.1.1']
listhost=['222.222.222.221','111.222.222.221'] # PING HOST
listgw=['10.0.1.250','10.0.1.254'] # GATEWAY HOST

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

	@staticmethod
	def _add_delete_cmd(command,gateway,ip):
		''' Returns proper iproute command arguments to add and delete routes '''
		cmd = 'route %s default gw %s' % (command, gateway)
		if ip is not None:
			cmd = 'route %s -host %s gw %s' % (command, ip, gateway)

		return cmd

	@staticmethod
	def add(gateway=None, ip=None):
		''' Adds a new route with corresponding properties. '''
		cmd = managegw._add_delete_cmd('add',gateway,ip)
		iproute(cmd)
		return cmd

	@staticmethod
	def delete(gateway=None,ip=None):
		''' Removes a route with corresponding properties. '''
		cmd = managegw._add_delete_cmd('del',gateway,ip)
		iproute(cmd)
		return cmd


#print  managegw(listgw).getactivegw()
#print  managegw(listgw).getothergw()
################ END CLASS managegw ##############

############### MISC FUNC ###############
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
def iproute(args):
		'''An iproute wrapper'''
		args_list = args.split()
		cmd =  args_list
		proc = subprocess.Popen(cmd,
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				close_fds=True)
		stdout_value, stderr_value = proc.communicate()
		if stderr_value:
			raise NameError(stderr_value)
		if stdout_value:
			return stdout_value

################ END FUNCTION IPROUTE  ##############

def main():
	pi = parseinput()
	verbmode = pi.options.verb
	a = ping(verbose=verbmode)
	pingresults = a.pinghost(listhost)
	resultcode = a.calcavaibility(pingresults,pi.options.warn,pi.options.crit)

	if statuscode(resultcode) > 1: # UTILIZZATO PER LE VERIFICHE DI CAMBIO GW
		''' PING TEST FAIL SET OTHERGW AND TEST OTHERGW'''
		activegw = managegw(listgw).getactivegw()
		othergw = managegw(listgw).getothergw()
		managegw.add(othergw)
		managegw.delete(activegw)
#		listhost1=['151.1.1.1','193.43.2.1','173.203.44.122','151.1.1.1']
		pingresults = a.pinghost(listhost)
		resultcode = a.calcavaibility(pingresults,pi.options.warn,pi.options.crit)
		if statuscode(resultcode) > 1:
			''' PING TEST FOR OTHERGW RESTORE CONFIG AND EXIT CRITICAL ERROR'''
			managegw.add(activegw)
			managegw.delete(othergw)
			print resultcode
			sys.exit(statuscode(' CRITICAL'))
	
	print resultcode
	sys.exit(statuscode(resultcode))

		

	

if __name__=="__main__":
	main()


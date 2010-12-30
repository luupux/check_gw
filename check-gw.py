from optparse import OptionParser
import os
import re
import time
import sys
__author__="Mauro Ferrigno"

DEBUG=0
listhost=['151.1.1.1','www.google.it','193.43.2.1','222.222.222.221','111.222.222.221']

class ping:
	def __init__(self,lifeline="NONE",report="NONE"):	
		self.lifeline = re.compile(r"(\d) received")
		self.report = ("No response","Partial Response","Alive")
		self.countok=[]

	def pinghost(self,listhost):
		self.listhost=listhost
		for host in self.listhost:
			ip = str(host)
			pingaling = os.popen("ping -w2 -q -c2 "+ip,"r")
			if DEBUG :
				print "Testing ",ip,
				sys.stdout.flush()
			while 1:
				line = pingaling.readline()
				if not line: break
				igot = re.findall(self.lifeline,line)
				if igot:
					if DEBUG :
						print self.report[int(igot[0])]
					if int(igot[0]) == 2:
						self.countok.append(host)
		return self.countok

	def calcavaibility(self,al,warn,crit):
		"""CALCOLA LA PERCENTUALE PER LE SOGLIE WARN E CRIT"""
		self.al = al
		self.crit = crit
		self.warn = warn
		pingok = float(len(self.al))
		ghost = float(len(self.listhost))
		result = '%.0f' %(round((pingok/ghost) *100))
		if DEBUG :
			print "WARN "+str(warn)
			print "CRIT "+str(crit)
			print "RESULT "+result

		if int(result) < int(crit):
			return "CRITICAL"

		if int(result) < int(warn):
			return "WARNING"

		return "OK"





class parseinput:
        def __init__(self,options=None,args=None):
                parser = OptionParser()
                parser.add_option("--warn",dest="warn",default="None",help="Warning  threshold")
                parser.add_option("--crit",dest="crit",default="None",help="Critical threshold")
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



def main():
	pi=parseinput()
	a=ping()
	pingresults=a.pinghost(listhost)
	print a.calcavaibility(pingresults,pi.options.warn,pi.options.crit)
	

	

if __name__=="__main__":
        main()


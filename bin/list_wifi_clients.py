#!/usr/bin/env python3

import sys, os, re, datetime
from optparse import OptionParser
import subprocess

def setupCmdLineArgs(cmdLineArgs):
  usage =\
"""\
%prog [-h|--help] [options]\
"""

  parser = OptionParser(usage)
                       
  help="verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)

  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)
  clo = cmdLineOptions

  if cmdLineOptions.verbose:
    print("cmdLineOptions:",cmdLineOptions)
    for index in range(0,len(cmdLineArgs)):
      print ("cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index]))

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  devices={}
  MACAdd = ""

  result = subprocess.run(['iw','wlan0','station','dump'],check=True,stdout=subprocess.PIPE)
  lines = bytes.decode(result.stdout).split(sep="\n")
  for line in lines:
    matchMAC       = re.search(r'Station\s+(..:..:..:..:..:..)',line)
    matchInactiveMs  = re.search(r'inactive time:\s+(\d+)\s+ms',line)
    matchConnectedSec = re.search(r'connected time:\s+(\d+)\s+seconds',line)
    
    if matchMAC:
      MACAdd = matchMAC.groups()[0]
      devices[MACAdd] = {}
    if matchInactiveMs:
      devices[MACAdd]["InactiveSec"] = int(matchInactiveMs.groups()[0])/1000.0
    if matchConnectedSec:
      seconds = int(matchConnectedSec.groups()[0])
      devices[MACAdd]["ConnectedTime"] = str(datetime.timedelta(seconds=seconds))

  if clo.verbose:
    print ("devices = ", devices)

  deviceInfo = {}
  dhcpLeases = open('/var/lib/misc/dnsmasq.leases','r')
  for line in dhcpLeases:
    info = line.split(" ")
    deviceInfo[info[1]] = {"Name":info[3],"IP":info[2]}

  if clo.verbose:
    print ("\n","deviceInfo = ",deviceInfo)

  for device in devices.values():
    device["Name"] = deviceInfo[MACAdd]["Name"] 
    device["IP"] = deviceInfo[MACAdd]["IP"] 

  if clo.verbose:
    print ("\n","devices = ", devices)

  print ("Connected devices:")
  for device in devices.values():
    name          = device["Name"]
    ip            = device["IP"]
    connectedTime = device["ConnectedTime"]
    inactiveSec   = device["InactiveSec"]
    msg = "%s: Connected for %s [h:m:s], Inactive for %s sec" % \
      (name, connectedTime, inactiveSec)
    print(msg)
    

if (__name__ == '__main__'):
  main(sys.argv[1:])


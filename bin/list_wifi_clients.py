#!/usr/bin/env python3

import sys, os, re, datetime
import texttable as tt
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

  for MACAdd, device in devices.items():
    device["Name"] = deviceInfo[MACAdd]["Name"]
    device["IP"]   = deviceInfo[MACAdd]["IP"] 

  if clo.verbose:
    print ("\n","devices = ", devices)

  connectedTable = tt.Texttable()
  headings = ['Name','IP','Connected Time (h:m:s)','Inactive Time (sec)']
  connectedTable.header(headings)
  connectedTable.set_cols_align(["l", "l", "c", "c"])
  names          = []
  ips            = []
  connectedTimes = []
  inactiveSecs   = []
  for device in devices.values():
    names          .append(device["Name"])
    ips            .append(device["IP"])
    connectedTimes .append(device["ConnectedTime"])
    inactiveSecs   .append(device["InactiveSec"])
  
  for row in zip(names,ips,connectedTimes,inactiveSecs):
    connectedTable.add_row(row)
    
  tableString = connectedTable.draw()
  print ("Connected devices:")
  print (tableString)

  dhcpLeaseTalble = tt.Texttable()
  headings = ['Name','IP','MAC','Connected']
  dhcpLeaseTalble.header(headings)
  dhcpLeaseTalble.set_cols_align(["l", "l", "l", "c"])
  names          = []
  ips            = []
  MACAdds        = []
  connecteds     = []
  for MACAdd, value in deviceInfo.items():
    names          .append(value["Name"])
    ips            .append(value["IP"])
    MACAdds        .append(MACAdd)
    connected = ""
    if MACAdd in devices:
      connected = "*"
    connecteds     .append(connected)


  for row in zip(names,ips,MACAdds,connecteds):
    dhcpLeaseTalble.add_row(row)
    
  tableString = dhcpLeaseTalble.draw()
  print ()
  print ("DHCP Leases:")
  print (tableString)    
  

if (__name__ == '__main__'):
  main(sys.argv[1:])


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

class ListWiFiClients(object):
  def __init__(self, verbose=False):
    self.verbose = verbose

    self.deviceInfo = None
    self.devices    = None

    self.reMAC          = re.compile(r'Station\s+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)')
    self.reInactiveMs   = re.compile(r'inactive time:\s+(\d+)\s+ms')
    self.reConnectedSec = re.compile(r'connected time:\s+(\d+)\s+seconds')

  def getData(self):

    deviceInfo = {}
    dhcpLeases = open('/var/lib/misc/dnsmasq.leases','r')
    for line in dhcpLeases:
      info = line.split(" ")
      deviceInfo[info[1]] = {"Name":info[3],"IP":info[2],
                             "InactiveSec":"-","ConnectedTime":"-"}

    if self.verbose:
      print ("\n","deviceInfo after reading dnsmasq.leases:","\n",deviceInfo)

    devices={}
    MACAdd = ""

    result = subprocess.run(['iw','wlan0','station','dump'],check=True,stdout=subprocess.PIPE)
    lines = bytes.decode(result.stdout).split(sep="\n")
    for line in lines:
      matchMAC          = reMAC         .search(line)
      matchInactiveMs   = reInactiveMs  .search(line)
      matchConnectedSec = reConnectedSec.search(line)

      errorMsg = ""
      
      if matchMAC:
        MACAdd = matchMAC.groups()[0]
        devices[MACAdd] = {"InactiveSec":"Not Found","ConnectedTime":"Not Found"}
      if matchInactiveMs:
        inactiveSec = int(matchInactiveMs.groups()[0])/1000.0
        if MACAdd in devices:
          devices[MACAdd]["InactiveSec"] = inactiveSec
        else:
          errorMsg = (MACAdd, "devices")
        if MACAdd in deviceInfo:
          deviceInfo[MACAdd]["InactiveSec"] = inactiveSec
        else:
          errorMsg = (MACAdd, "deviceInfo")
      if matchConnectedSec:
        connectedSec = int(matchConnectedSec.groups()[0])
        connectedTime = str(datetime.timedelta(seconds=connectedSec))
        if MACAdd in devices:
          devices[MACAdd]["ConnectedTime"] = connectedTime
        else:
          errorMsg = (MACAdd, "devices")
        if MACAdd in deviceInfo:
          deviceInfo[MACAdd]["ConnectedTime"] = connectedTime
        else:
          errorMsg = (MACAdd, "deviceInfo")

      if errorMsg:
        print("Error: Could not find key %s in dictionary '%s'" \
              % (errorMsg[0],errorMsg[1]))

    if self.verbose:
      print ("\n","devices after executing iw command:","\n",devices)

    if self.verbose:
      print ("\n","deviceInfo after adding inactive and connected time ",
             deviceInfo)

    for MACAdd, device in devices.items():
      device["Name"] = deviceInfo[MACAdd]["Name"]
      device["IP"]   = deviceInfo[MACAdd]["IP"] 

    if self.verbose:
      print ("\n","device after adding name and ip:","\n",device)

    self.deviceInfo = deviceInfo
    self.devices    = devices
      
  def createDevicesTable(self):
    connectedTable = tt.Texttable()
    headings = ['Name','IP','Connected Time (h:m:s)','Inactive Time (sec)']
    connectedTable.header(headings)
    connectedTable.set_cols_align(["l", "l", "c", "c"])
    names          = []
    ips            = []
    connectedTimes = []
    inactiveSecs   = []
    for device in self.devices.values():
      names          .append(device["Name"])
      ips            .append(device["IP"])
      connectedTimes .append(device["ConnectedTime"])
      inactiveSecs   .append(device["InactiveSec"])
  
    for row in zip(names,ips,connectedTimes,inactiveSecs):
      connectedTable.add_row(row)

    self.connectedTable = connectedTable
      
  def printDevicesTable(self,stream=sys.stdin):
    tableString = self.connectedTable.draw()
    print(tableString, file=stream)

  def createDeviceInfoTable(self):
    dhcpLeaseTalble = tt.Texttable()
    headings = ['Name','IP','MAC','Connected Time (h:m:s)','Inactive Time (sec)']
    dhcpLeaseTalble.header(headings)
    dhcpLeaseTalble.set_cols_align(["l", "l", "l", "c","c"])
    dhcpLeaseTalble.set_cols_width([10,12,17,14,10])
    names          = []
    ips            = []
    MACAdds        = []
    connectedTimes = []
    inactiveSecs   = []
    for MACAdd, value in sorted(deviceInfo.items()):
      names          .append(value["Name"])
      ips            .append(value["IP"])
      MACAdds        .append(MACAdd)
      connectedTimes .append(value["ConnectedTime"])
      inactiveSecs   .append(value["InactiveSec"])

    for row in zip(names,ips,MACAdds,connectedTimes,inactiveSecs):
      dhcpLeaseTalble.add_row(row)

    self.dhcpLeaseTalble = dhcpLeaseTalble
    
  def printDeviceInfoTable(self,stream):
    tableString = dhcpLeaseTalble.draw()
    print(tableString, file=stream)

if (__name__ == '__main__'):
  main(sys.argv[1:])

  print ()
  print ("Connected devices:")
  print ("DHCP Leases:")
  


  


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

    self.dhcpLeases      = None
    self.conDevices      = None
    self.conDevicesTable = None
    self.dhcpLeasesTable = None

    self.reMAC          = re.compile(r'Station\s+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)')
    self.reInactiveMs   = re.compile(r'inactive time:\s+(\d+)\s+ms')
    self.reConnectedSec = re.compile(r'connected time:\s+(\d+)\s+seconds')

  def loadData(self):
    dhcpLeases = {}
    dhcpLeasesFile = open('/var/lib/misc/dnsmasq.leases','r')
    for line in dhcpLeasesFile:
      info = line.split(" ")
      dhcpLeases[info[1]] = {"Name":info[3],"IP":info[2],
                             "ConnectedTime":"Not Connected",
                             "InactiveSec":"-"}

    dhcpLeasesFile.close()

    if self.verbose:
      print ("\n","dhcpLeases after reading dnsmasq.leases:","\n",dhcpLeases)

    conDevices={}
    MACAdd = ""

    result = subprocess.run(['iw','wlan0','station','dump'],check=True,stdout=subprocess.PIPE)
    lines = bytes.decode(result.stdout).split(sep="\n")
    for line in lines:
      matchMAC          = self.reMAC         .search(line)
      matchInactiveMs   = self.reInactiveMs  .search(line)
      matchConnectedSec = self.reConnectedSec.search(line)

      errorMsg = ""
      
      if matchMAC:
        MACAdd = matchMAC.groups()[0]
        conDevices[MACAdd] = {"InactiveSec":"Not Found","ConnectedTime":"Not Found"}
      if matchInactiveMs:
        inactiveSec = int(matchInactiveMs.groups()[0])/1000.0
        if MACAdd in conDevices:
          conDevices[MACAdd]["InactiveSec"] = inactiveSec
        else:
          errorMsg = (MACAdd, "conDevices")
        if MACAdd in dhcpLeases:
          dhcpLeases[MACAdd]["InactiveSec"] = inactiveSec
        else:
          errorMsg = (MACAdd, "dhcpLeases")
      if matchConnectedSec:
        connectedSec = int(matchConnectedSec.groups()[0])
        connectedTime = str(datetime.timedelta(seconds=connectedSec))
        if MACAdd in conDevices:
          conDevices[MACAdd]["ConnectedTime"] = connectedTime
        else:
          errorMsg = (MACAdd, "conDevices")
        if MACAdd in dhcpLeases:
          dhcpLeases[MACAdd]["ConnectedTime"] = connectedTime
        else:
          errorMsg = (MACAdd, "dhcpLeases")

      if errorMsg:
        print("Error: Could not find key %s in dictionary '%s'" \
              % (errorMsg[0],errorMsg[1]))

    if self.verbose:
      print ("\n","conDevices after executing iw command:","\n",conDevices)

    if self.verbose:
      print ("\n","dhcpLeases after adding inactive and connected time ",
             dhcpLeases)

    for MACAdd, device in conDevices.items():
      device["Name"] = dhcpLeases[MACAdd]["Name"]
      device["IP"]   = dhcpLeases[MACAdd]["IP"] 

    if self.verbose:
      print ("\n","device after adding name and ip:","\n",device)

    self.dhcpLeases = dhcpLeases
    self.conDevices = conDevices
      
  def createConDevicesTable(self):

    if not self.conDevices:
      self.loadData()

    conDevicesTable = tt.Texttable()
    headings = ['Name','IP','Connected Time (h:m:s)','Inactive Time (sec)']
    conDevicesTable.header(headings)
    conDevicesTable.set_cols_align(["l", "l", "c", "c"])
    names          = []
    ips            = []
    connectedTimes = []
    inactiveSecs   = []
    for device in self.conDevices.values():
      names          .append(device["Name"])
      ips            .append(device["IP"])
      connectedTimes .append(device["ConnectedTime"])
      inactiveSecs   .append(device["InactiveSec"])
  
    for row in zip(names,ips,connectedTimes,inactiveSecs):
      conDevicesTable.add_row(row)

    self.conDevicesTable = conDevicesTable
      
  def createDHCPLeasesTable(self):

    if not self.dhcpLeasesTable:
      self.loadData()

    dhcpLeasesTable = tt.Texttable()
    headings = ['Name','IP','MAC','Connected Time (h:m:s)','Inactive Time (sec)']
    dhcpLeasesTable.header(headings)
    dhcpLeasesTable.set_cols_align(["l", "l", "l", "c","c"])
    dhcpLeasesTable.set_cols_width([10,12,17,14,10])
    names          = []
    ips            = []
    MACAdds        = []
    connectedTimes = []
    inactiveSecs   = []
    for MACAdd, value in sorted(self.dhcpLeases.items()):
      names          .append(value["Name"])
      ips            .append(value["IP"])
      MACAdds        .append(MACAdd)
      connectedTimes .append(value["ConnectedTime"])
      inactiveSecs   .append(value["InactiveSec"])

    for row in zip(names,ips,MACAdds,connectedTimes,inactiveSecs):
      dhcpLeasesTable.add_row(row)

    self.dhcpLeasesTable = dhcpLeasesTable
    
  def getConDevicesTableString(self):
    if not self.conDevicesTable:
      self.createConDevicesTable()
    return self.conDevicesTable.draw()

  def printConDevicesTable(self,stream=sys.stdout):
    tableString = self.getConDevicesTableString()
    print(tableString, file=stream)

  def getDHCPLeasesTableString(self):
    if not self.dhcpLeasesTable:
      self.createDHCPLeasesTable()
    return self.dhcpLeasesTable.draw()

  def printDHCPLeasesTable(self,stream=sys.stdout):
    tableString = self.getDHCPLeasesTableString()
    print(tableString, file=stream)

if (__name__ == '__main__'):
  (clo, cla) = setupCmdLineArgs(sys.argv[1:])

  myListWiFiClients = ListWiFiClients(clo.verbose)

  print ("Connected conDevices:")
  myListWiFiClients.printConDevicesTable()

  print ()
  print ("DHCP Leases:")
  myListWiFiClients.printDHCPLeasesTable()

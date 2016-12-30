#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
from subprocess import call

def setupCmdLineArgs(cmdLineArgs):
  usage =\
"""
usage: %prog [-h|--help] [options] message file_1 [file_2 ...]
       where:
         -h|--help to see options

       Executes:
       git commit -m 'file_1: message' file_1
       git commit -m 'file_1, file_2: message' file_1 file_2
       git commit -m 'file_1, file_2, file_3: message' file_1 file_2 file_3
       ...

       NOTE: message is quoted with \", so use \' for quotes in the message.
"""

  parser = OptionParser(usage)
                       
  help="verbose mode."
  parser.add_option("-v", "--verbose",
                    action="store_true", default=False,
                    dest="verbose",
                    help=help)

  help="No operation, just echo commands"
  parser.add_option("-n", "--noOp",
                    action="store_true", 
                    default=False,
                    dest="noOp",
                    help=help)

  help="Quiet mode.  Do not ask for conformation or echo any information"
  parser.add_option("-q", "--quiet",
                    action="store_true", 
                    default=False,
                    dest="quiet",
                    help=help)
  
  (cmdLineOptions, cmdLineArgs) = parser.parse_args(cmdLineArgs)
  clo = cmdLineOptions

  if cmdLineOptions.verbose:
    print "cmdLineOptions:",cmdLineOptions
    for index in range(0,len(cmdLineArgs)):
      print "cmdLineArgs[%s] = '%s'" % (index, cmdLineArgs[index])

  if len(cmdLineArgs) < 2:
    parser.error("A message and at least one file must be specified on the "+\
    "command line")

  return (cmdLineOptions, cmdLineArgs)

def main(cmdLineArgs):
  (clo, cla) = setupCmdLineArgs(cmdLineArgs)

  message  = cla[0]
  fileList = cla[1:]

  if clo.verbose:
    print "message: ", message
    print "fileList:", fileList

  msg = '"' + ", ".join(fileList) + ": " + message + '"'

  cmdList = ["git","commit","-m"]
  cmdList.append(msg)
  cmdList += fileList

  cmd = " ".join(cmdList)

  execute = True
  if not clo.quiet:
    print "Command is:"
    print cmd
    answer = raw_input("Execute [y/n]? ")
    if not answer:
      answer = "n"
    if answer[0].lower() != 'y':
      execute = False
      print "Exiting..."
  elif clo.verbose:
    print "Command:"
    print cmd

  cmdText = "call(%s)" % cmdList
  if execute:
    if not clo.noOp:
      if clo.verbose:
        print "Executing:"
        print cmdText
      print
      call(cmdList)
    else:
      print "Would have made the call:"
      print cmdText

if (__name__ == '__main__'):
  main(sys.argv[1:])

#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

#Ptyhon Http Secure Path Tools

from phspdb import phspdb
from getopt import getopt
import sys

class phsptools:
  def __init__(self):
    self.db = phspdb()

    # Commandline arguments
    self.cmds= [ (self.Help, "help", []),
                 (self.AddHttps, "addhttps", [("str","urlExt"), ("str","scriptPath"), ("num","default-rights")]),
                 (self.AddUser, "adduser", [("str","userName")]),
                 (self.Init, "init", []),
                 (self.Grant, "grant", [("str","userName"), ("str","urlExt"), ("num","rights")]),
                 (self.RmHttps, "rmhttps", [("str","urlExt")]),
                 (self.RmUser, "rmuser", [("str","userName")]),
                 (self.Info, "dbinfo", []) ]


  #def AddHttps(self, urlExt, scriptPath, rights = self.db.HTTPS_DEFAULT_NONE):
  def AddHttps(self, urlExt, scriptPath, rights):
    self.db.addHttps(scriptPath, urlExt, rights)
    print "https %s sucesfully added."%urlExt

  def AddUser(self, userName):
    #print "adding user:", userName
    #certName = self.db.UserName2CertPath(userName)
    #print "user certificate name: \"%s\""%certName
    #self.db.addUser(certName)
    self.db.addUser(userName)
    print "User %s sucesfully added."%userName

  def Init(self):
    print "Initialize database"
    self.db.Init()
    print "Database sucessfully created."

  def Grant(self, userName, urlExt, rights):
    certName = self.db.UserName2CertPath(userName)
    userId = self.db.user(certName)
    (httpsId, script_path, url_ext, default) = self.db.https(urlExt)

    certName = self.db.UserName2CertPath(userName)
    userId = self.db.userIdByCert(certName)

    if rights == self.db.HTTPS_DEFAULT_NONE:
      # Remove access record, default rights are used
      self.db.rmAccess(httpsId, userId)
      print "Remove user %s rights, default used."%(userName)
    else:
      res = self.db.https(urlExt)
      if len(res) == 0:
        raise Exception("http not found")
      httpsId = res[0]

      self.db.addAccess(httpsId, userId, rights)
      print "User %s rights %d sucesfully changed."%(userName, rights)

  def RmHttps(self, urlExt):
    # Remove all accesses
    accesses = self.db.accessHttps(urlExt)
    for (accessId, userId, httpsId, rights) in accesses:
      self.db.rmAccess(httpsId, userId)

    # Remove Https
    self.db.rmHttps(urlExt)
    print "Http %s sucesfully removed."%urlExt

  def RmUser(self, userName):
    res = self.db.accessUser(userName)
    if len(res) == 0:
      print "user %s not found"%userName
    else:
      (accessId, userId, httpsId, rights) = res
      self.db.rmAccess(httpsId, userId)
      self.db.rmUser(userName)
      print "User %s sucesfully removed."%userName

  def Info(self):
    tables = self.db.Tables()

    if len(tables) == 0:
      print "No tables found in database."
    else:
      for table in tables:
        print table[0]
        for column in table[1]:
          print "  %s %s"%(column[0], column[1])
        print ""

    accesses = self.db.accesses()
    if len(accesses) > 0:
      print "access_id, user, cert, https, rights"
      for access in accesses:
        (access_id, userId, httpsId, rights) = access
        user = self.db.userName(userId)
        cert = self.db.UserName2CertPath(user)
        (https_id, cert_id, https, rightsDefault) = self.db.httpsById(httpsId)
        print access_id, user, cert, https, rights

  def Help(self):
    opts = []
    for (func, option, help) in self.cmds:
      opts.append(option)
    print "usage: python phsptools.py --%s"%opts


if __name__ == "__main__":
  tools = phsptools()
  #         (function, command-name, argument-list[(type, name)])

  opts = []
  for (func, option, help) in tools.cmds:
    opts.append(option)

  try:
    optlist, args = getopt(sys.argv[1:], "", opts)
  except Exception:
    print "no valid command found, use "--" as command prefix"
    tools.Help()
    exit()

  #print optlist, args

  if len(optlist) == 0:
    print "no valid command found"
    tools.Help()
    exit()

  optPos = 0
  while optPos<len(opts) and opts[optPos]!=optlist[0][0][2:]:
    optPos = optPos + 1

  #no command found, exit
  if optPos == len(opts):
    print "command not found"
    tools.Help()
    exit()

  #command found
  (func, option, help) = tools.cmds[optPos]

  #invalid argument count
  if len(help) != len(args):
    print "%s invalid arguments, %d required, but %d given."%(option, len(help), len(args))
    print "  arguments:", help
    exit()

  #prepare and check arguments
  funcArgs = []
  if len(args) > 0:
    #args.insert(0, optlist[optPos][1])   #1st argumet
    for argPos in range(0, len(args)):
      (type, name) = help[argPos]
      if type == "str":
        funcArgs.append(args[argPos])
      elif type == "num":
        funcArgs.append(int(args[argPos]))
      else:
        tools.Help()
        exit()

  #call the function
  t = tuple(funcArgs)
  func(*t)

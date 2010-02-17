'''
SimpleSecureHTTPServer.py - simple HTTP server supporting SSL.

- replace fpem with the location of your .pem server file.
- the default port is 443.

usage: python SimpleSecureHTTPServer.py
'''
import socket, os
from SocketServer import BaseServer
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from OpenSSL import SSL

from phspdb import phspdb
import imp
import sys
import os
import cgi

from serverAddress import serverAddress


##################################################################
# HTTPS SERVER

def verify_cb(conn, cert, errnum, depth, ok):
  # This obviously has to be updated
  print 'Got certificate: %s' % cert.get_subject()
  print "(conn, cert, errnum, depth):", conn, cert, errnum, depth
  print "preverify errnum: %d, depth: %d, ok: %d"%(errnum, depth, ok)

  global g_cert
  g_cert = cert.get_subject()

  return ok

class SecureHTTPServer(HTTPServer):
  def __init__(self, server_address, HandlerClass):
    BaseServer.__init__(self, server_address, HandlerClass)
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    fpem = 'ssl/certs/server.pem'
    ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb) 
    ctx.set_verify_depth(4)
    ctx.use_privatekey_file (fpem)
    ctx.use_certificate_file(fpem)
    ctx.load_verify_locations(fpem)

    self.socket = SSL.Connection(ctx, socket.socket(self.address_family, self.socket_type))
    self.server_bind()
    self.server_activate()


class SecureHTTPRequestHandler(SimpleHTTPRequestHandler):
  def setup(self):
    self.connection = self.request
    self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
    self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)


##################################################################
# PATH RESOLVER HTTP SERVER

class PathHTTPHandler(SecureHTTPRequestHandler):
  def __init__(self, request, client_address, server):
    SecureHTTPRequestHandler.__init__(self, request, client_address, server)

  #post and get request resolvers
  def do_GET(self):
    (scriptPath, rights, urls) = self.Resolve()
    if rights == db.HTTPS_NONE:
      (scriptPath, rights) = self.Denied()
    print "GET import (scriptPath, rights):", scriptPath, rights

    (module, className) = self.load_from_file(scriptPath)
    server = getattr(module, className)()
    print "GET execute server class:", className

    res = server.do_GET(urls)

    if len(res[0]) == 1:
      defHead = []
      defHead.append( ("Content-type", "text/html") )
      body = res
      headers = defHead
    else:
      body = res[0]
      headers = res[1]

    print "http reply(%d): headers: \"%s\""%(len(body), headers)
    self.sendPage(headers, body)


  def do_POST(self):
    #(scriptPath, rights, urls) = self.Resolve()
    (scriptPath, rights, urls) = self.Resolve()
    if rights == db.HTTPS_NONE:
      (scriptPath, rights) = self.Denied()
    print "POST import (scriptPath, rights):", scriptPath, rights

    # Parse the form data posted
    form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

    (module, className) = self.load_from_file(scriptPath)
    server = getattr(module, className)()
    print "POST execute server class:", className

    res = server.do_POST(urls, form)

    if len(res[0]) == 1:
      defHead = []
      defHead.append( ("Content-type", "text/html") )
      body = res
      headers = defHead
    else:
      body = res[0]
      headers = res[1]

    print "http reply(%d): headers: \"%s\""%(len(body), headers)
    self.sendPage(headers, body)


  #form http reply
  def sendPage(self, headers, body):
    try:
      self.send_response( 200 )

      for head in headers:
        self.send_header(head[0], head[1])

      self.send_header( "Content-length", str(len(body)) )
      #self.send_header( "Session-ID", str(00001324) )
      self.send_header( "Pragma", "no-cache" )
      #self.send_header( "Cache-Control", "no-cache, no-store, must-revalidate, post-check=0, pre-check=0" )
      self.send_header( "Cache-Control", "no-cache, must-revalidate" )
      self.send_header( "Expires", "Sat, 26 Jul 1997 05:00:00 GMT" )

      self.end_headers()
      self.wfile.write( body )
    except:
      print sys.exc_info()
      print "--------------------"
      pass


  #target script and user rights and url resolver
  #  input:
  #  out: target python script path, client rights, url tuple server/script/page
  def Resolve(self):
    #split url to server/script/page parts as tuple u
    pageUrl = ""
    end = self.path[1:].find("/")
    if end == -1:
      scriptName = self.path
      scriptUrl = self.path[1:] + "/"
    else:
      scriptName = self.path[:end +1]
      scriptUrl = self.path[1:end +1] + "/"
      pageUrl = self.path[end+2:]

    #get server url based on client network
    self.serverUrl = serverAddress(self.client_address)

    #create url tuple
    u = (self.serverUrl, scriptUrl, pageUrl)

    global g_cert
    print "--------------------"
    print "self.path:", self.path
    print "req url:",u
    print "scriptName :", scriptName
    print "user:", g_cert.commonName
    print "self.client_address:", self.client_address

    res = db.httpsRaw(scriptName)
    if len(res) == 0:
      print "script url: \"%s\" not found, redirected to denied"%scriptName
      denied = self.Denied()
      return (denied[0], denied[1], u);

    (httpsId, scriptPath, urlExt, defaultRights) = res[0]

    scriptPathList = scriptPath.split("\\")
    scriptPath = os.sep.join(scriptPathList)

    if False == os.path.exists(scriptPath):
      print "file \"%s\" not found, redirect to denied"%scriptPath
      denied = self.Denied()
      return (denied[0], denied[1], u);

    res = db.userRaw(g_cert.commonName)
    if len(res) > 0:
      (userId, certPath) = res[0]
      res = db.accessRaw(httpsId, userId)
      if len(res) > 0:
        (accessId, userId, httpsId, userRights) = res[0]
        return (scriptPath, userRights, u)

    return (scriptPath, defaultRights, u)


  #default script not found or no rights, redirect to 'denied' script
  def Denied(self):
    res = db.https("denied")
    if len(res) == 0:
      raise Exception("No 'denied' script found, use phsptools.py --addhttps \"denied\".")

    (httpsId, scriptPath, urlExt, defaultRights) = res

    scriptPathList = scriptPath.split("\\")
    scriptPath = os.sep.join(scriptPathList)

    return (scriptPath, defaultRights)


  #dynamic http server class load
  #  the server class name must be HTTPServer
  #  return module and class name
  def load_from_file(self, filepath):
    #try:
    #  try:
    if True:
        class_inst = None

        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        print "loading module:", mod_name

        if file_ext.lower() == '.py':
          py_mod = imp.load_source(mod_name, filepath)

        elif file_ext.lower() == '.pyc':
          py_mod = imp.load_compiled(mod_name, filepath)

        expected_class = mod_name
        if expected_class in dir(py_mod):
          return py_mod, mod_name

    #  finally:
    #    try: fin.close()
    #    except: pass

    #except ImportError, x:
    #  traceback.print_exc(file = sys.stderr)
    #  raise

    #except:
    #  traceback.print_exc(file = sys.stderr)
    #  raise

    return class_inst


##################################################################
# TEST

def test(HandlerClass = PathHTTPHandler, ServerClass = SecureHTTPServer):
  print "open db ..."
  global db
  db = phspdb()

  server_address = ('', 8080) # (address, port)
  httpd = ServerClass(server_address, HandlerClass)
  sa = httpd.socket.getsockname()
  print "Serving HTTPS on", sa[0], "port", sa[1], "..."
  httpd.serve_forever()


if __name__ == '__main__':
  test()

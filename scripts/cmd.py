#stateless shell interface

import os
import sys
#import subprocess
from commands import *

class cmd:
  def __init__(self):
    self.historyDepth = 35
    return

  #process get request
  def do_GET(self, urls):
    history = ""
    path = sys.path[0]
    return self.Body(urls[0]+urls[1], history, "", path)

  #process post request
  def do_POST(self, urls, form):
    history = ""
    path = ""
    body = ""
    result = ""
    command = ""

    for field in form.keys(): 
      field_item = form[field]
      data = []
      if type(field_item) == type([]): data = field_item
      else: data.append(field_item)

      for mini in data:
        print "mini:", mini.name, mini.value

        if mini.name == "history":
          history = mini.value

        elif mini.name == "path":
          path = mini.value

        elif mini.name == "command":
          command = mini.value

    if len(command) == 0:
      return self.do_GET()

    result = self.doCmd(command, path)
    (history, out) = self.Output(history, result, command)

    return self.Body(urls[0]+urls[1], history, out, path)


  #execute shell command
  def doCmd(self, cmd, path):
    #return os.system(cmd)

    #p2 = subprocess.Popen([cmd], stdout = subprocess.PIPE)
    #return p2.stdout.read()

    #in = os.popen("cmd", "w")
    #in.write(cmd)

    #i = os.popen('dir')
    #print i

    print 'Running: "%s"' % cmd
    ##status, text = getstatusoutput(cmd)
    #text = getoutput(cmd)
    ##exit_code = status >> 8 # high byte
    ##signal_num = status % 256 # low byte
    ##print 'Status: x%04x' % status
    ##print 'Signal: x%02x (%d)' % (signal_num, signal_num)
    ##print 'Exit  : x%02x (%d)' % (exit_code, exit_code)
    ##print 'Core? : %s' % bool(signal_num & (1 << 8)) # high bit
    #print 'Output:'
    #print text
    #return text

    import subprocess
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)  
    output = "".join(pipe.stdout.readlines()) 
    sts = pipe.returncode
    if sts is None: sts = 0
    return output


  #generate response body
  def Body(self, url, history, text, path):
    body = "<P>"
    body += text
    body += "</P><BR>\n<FORM ACTION=\"%s\" METHOD=POST>\n" % url

    body += "<INPUT TYPE=\"HIDDEN\" NAME=\"history\" VALUE=\"%s\">\n" % history
    body += "<INPUT TYPE=\"HIDDEN\" NAME=\"path\" VALUE=\"%s\">\n" % path

    body += "%s # <INPUT TYPE=\"TEXT\" NAME=\"command\"><BR>\n" % path
    body += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Send\"></FORM>"

    return body

  # generate output text and update history
  def Output(self, history, result, command):
    result = result.split("<")
    result = "[".join(result)
    result = result.split(">")
    result = "]".join(result)

    history = history + "#" + command + "\n"
    history = history + result

    #format output text
    out = history.splitlines()

    #truncate empty lines 
    linePos = 0
    second = False
    for line in out:
      if len(line) == 0:
        if second == False:
          #print linePos, ": first"
          second = True
        else:
          #print linePos, ": remove"
          del out[linePos]
      else:
        second = False
        #print linePos, ": OK- (", len(line), "): \"", line, "\""
        linePos = linePos + 1

    # truncate invisible lines
    out = out[len(out) - self.historyDepth:]
    out = "<BR>\n".join(out)

    #print "-out----------\n", out
    #if len(result.splitlines()) > self.historyDepth:
    #  out = "... result cuted (max %s lines)<BR>\n %s"%(self.historyDepth, out)

    return (history, out)
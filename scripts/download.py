#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

#file downloader
import os

class download:
  def __init__(self):
    self.filePath = ""
    self.fileName = ""
    self.defaultPath = os.curdir
    return

  def do_GET(self, urls):
    self.url = urls[0]+urls[1]
    return self.BodySelectFile(self.defaultPath)

  def do_POST(self, urls, form):
    self.url = urls[0]+urls[1]
    filePost = ""
    fileName = ""

    #parse post data
    for field in form.keys():
      field_item = form[field]
      data = []
      if type(field_item) == type([]): data = field_item
      else: data.append(field_item)

      for mini in data:
        if mini.name == "file":
          filePost = mini.value

    #build http reply
    if len(filePost) == 0:
      return self.BodySelectFile(self.defaultPath);

    else:
      if os.path.isdir(filePost):
        filePath = filePost
        return self.BodySelectFile(filePath);

    sep = filePost.rfind(os.sep)
    self.filePath = filePost[:sep+1]
    self.fileName = filePost[sep+1:]

    print "filePost:", filePost
    print "separator:", sep
    print "fileName:", self.fileName
    print "filePath:", self.filePath

    #send the file when known
    return self.AttachFile(self.filePath, self.fileName)


  #select file and path form
  def BodySelectFile(self, path):
    body = "<FORM ACTION=\"%s\" METHOD=\"POST\">\n" % self.url

    body += "[CURRENT PATH]: %s<BR>\n" % path
    body += "<P>"

    xlist = []
    dlist = os.listdir(path)
    for d in dlist:
      if os.path.isdir(path + os.sep + d):
        xlist.append("[DIR] " + d)
      else:
        xlist.append(d)

    body += "<BR>\n  ".join(xlist)
    body += "</P>"

    body += "File : <INPUT TYPE=\"TEXT\" NAME=\"file\" size=\"90%\">\n"
    body += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Send\"></FORM>"

    return body


  #send file to client
  def AttachFile(self, filePath, fileName):
    #read binary file
    file = open(filePath + fileName, 'rb')
    body = file.read()
    file.close()

    #attach http headers
    headers = []
    headers.append( ("Content-type", "application/octet-stream") )
    content = "attachment; filename=%s modification-date=\"Wed, 12 Feb 1997 16:29:51 -0666\"" % fileName
    headers.append( ("Content-disposition", content) )

    return (body, headers)

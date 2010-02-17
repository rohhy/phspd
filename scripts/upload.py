#file uploader
import os


class upload:
  def __init__(self):
    self.pathDefault = "c:\\tmp"
    return

  def do_GET(self, urls):
    return self.Body(urls[0]+urls[1])

  def do_POST(self, urls, form):
    name = ""
    data = ""
    path = ""

    for field in form.keys():
      field_item = form[field]
      data = []
      if type(field_item) == type([]): data = field_item
      else: data.append(field_item)

      for mini in data:
        if mini.name == "file":
          data = mini.value
          name = mini.filename
        elif mini.name == "path":
          path = mini.value

    #write received file
    if len(data) > 0 and len(name) > 0:
      if len(path) == 0:
        name = self.pathDefault + os.sep + name
      else:
        name = path + os.sep + name

      print "Write to file \"%s\" %d bytes."%(name, len(data))
      fw = open(name,"w")
      fw.write(data)
      fw.close()
    else:
      print "No file received."

    return self.Body(urls[0]+urls[1])

  #generate response body
  def Body(self, url):
    body = "<FORM ACTION=\"%s\" METHOD=\"POST\" ENCTYPE=\"multipart/form-data\">\n" % url
    body += "Server path : <INPUT TYPE=\"TEXT\" NAME=\"path\" size=\"45\"><BR>\n"
    body += "File : <INPUT TYPE=\"FILE\" NAME=\"file\" size=\"30\">"
    body += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Send\"></FORM>"

    return body


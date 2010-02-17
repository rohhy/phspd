# reality scanner database web interface module for phspd https server

realModulesPath = "c:\\tmp\\py\\real\\next\\"

#import real modules
sys.path.append(realModulesPath)
from realdb import realdb

class realWeb:
  def __init__(self):
    self.db = realdb(realModulesPath"real.db")


  def do_GET(self, urls):
    return self.Page()


  def do_POST(self, urls):
    return self.Page()


  def Page(self):
    page = "<HTML><BODY>"
    page += self.Body()
    page += "</BODY></HTML>"

    return page


  def Body(self):
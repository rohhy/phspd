#access denied page

class denied:
  def __init__(self):
    self.msg = "error 404: access denied"

  def do_GET(self, urls):
    return self.msg

  def do_POST(self, urls, form):
    return self.msg
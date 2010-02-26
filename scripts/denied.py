#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

#access denied page

class denied:
  def __init__(self):
    self.msg = "error 404: access denied"

  def do_GET(self, urls):
    return self.msg

  def do_POST(self, urls, form):
    return self.msg

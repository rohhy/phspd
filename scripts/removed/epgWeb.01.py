#dvb-t epg database interface

import string,cgi,time
import traceback,sys #error handling
from os import curdir, sep, system
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import sqlite3
import sys


class epgWeb:
    def __init__(self):
      self.ip = "https://localhost"   #"84.19.66.153:8080"   #"10.0.3.101:8080"
      self.cardsCount = 2
      self.epgDBPath = "/root/epg/epg.db"

      print "connecting epg db..."
      self.connection = sqlite3.connect(self.epgDBPath)
      self.cursor = self.connection.cursor()
      return

    def __del__(self):
      self.connection.close()

    #search all service names
    def listServices(self):
      sql = "SELECT service FROM SERVICE"
      self.cursor.execute(sql)
      return self.cursor.fetchall()

    def do_GET(self, url):
      self.url = url[1:]
      scriptUrlStart = url[1:].find("/") +1
      print "scriptUrlStart", scriptUrlStart
      if scriptUrlStart <= len(url):
        self.scriptUrl = ""
      else:
        self.scriptUrl = url[1 : scriptUrlStart] + "/"

      print "ip:%s, url:%s, scriptUrl:%s"%(self.url, url, self.scriptUrl)
      sel = self.chkURL(self.scriptUrl)
      if sel == None:
        self.sel_date = time.time()
        self.sel_service = self.listServices()[0][0]
      else:
        (self.sel_service, self.sel_date) = sel
      body = self.Page()
      return body

    def do_POST(self, url, form):
        self.url = url[1:]
        scriptUrlStart = url[1:].find("/") +1
        print "scriptUrlStart", scriptUrlStart
        if scriptUrlStart <= len(url):
          self.scriptUrl = ""
        else:
          self.scriptUrl = url[1 : scriptUrlStart] + "/"

        sel = self.chkURL(self.scriptUrl)
        if sel == None:
          self.sel_date = time.time()
          self.sel_service = self.listServices()[0][0]
        else:
          (self.sel_service, self.sel_date) = sel

        service = self.sel_service

        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        program = "Form data:<BR>\n"

        #find changes
        setrec = []
        rmrec = []

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            data = []
            if type(field_item) == type([]): data = field_item
            else: data.append(field_item)

            for mini in data:
              report = "name:%s value:%s<BR>\n"%(mini.name, mini.value)
              #self.wfile.write(report)
              program = program + report

              service=""
              start=0
              if mini.name == "epgset":
                delim = mini.value.find(".")
                service = mini.value[0 : delim]
                start = mini.value[delim+1 : len(mini.value)]

                #pokud je v rmrec, tak ji pouze vyjmi
                found = False
                for pos in range(len(rmrec)):
                  if start == rmrec[pos]:
                    found = True
                    rmrec.remove(start)
                    break
                if found == False:
                #pridej do setrec pokud neni v rmrec (= byla uvedena jako epgpreset ale nebyla jeste nalezena epgset)
                  for pos in range(len(setrec)):
                    if start == setrec[pos]:
                      found = True
                      break
                  if found == False:
                    setrec.append(start)

              elif mini.name == "epgpreset":
                delim = mini.value.find(".")
                service = mini.value[0 : delim]
                start = mini.value[delim+1 : len(mini.value)]

                #pokud je v setrec, tak ji pouze vyjmi
                found = False
                for pos in range(len(setrec)):
                  if start == setrec[pos]:
                    found = True
                    setrec.remove(start)
                    break
                if found == False:
                #pridej do rmrec pokud neni v setrec (pokud je v set nic se nemeni, pokud neni mozna jeste set nebylo nalezeno)
                  for pos in range(len(rmrec)):
                    if start == rmrec[pos]:
                      found = True
                      break
                  if found == False:
                    rmrec.append(start)

        #encode service
        ret = ""
        sql = "SELECT * FROM SERVICE WHERE service==\"%s\""%(service)
        self.cursor.execute(sql)
        ret = self.cursor.fetchall()

        if len(ret) == 0:
          self.errorX()
          return "error<br>"
        service_id = ret[0][0]

        #execute changes
        for item in setrec:
          print "set    start:%s, service:%s:(id:%d)"%(item, service, service_id)
          sql = "UPDATE EPG SET recording=1 WHERE service_id=\"%s\" and start_tm==%d;"%(service_id, int(item))
          self.cursor.execute(sql)

        for item in rmrec:
          print "rm     start:%s, service:%s:(id:%d)"%(item, service, service_id)
          sql = "UPDATE EPG SET recording=0 WHERE service_id=\"%s\" and start_tm==%d;"%(service_id, int(item))
          self.cursor.execute(sql)

        self.connection.commit()

        #reload recording
        if len(rmrec)>0 or len(setrec)>0:
          print "reload recording..."
          system("kill -10 $(./epgRecPID.sh)")

        #generate a html page
        body = self.Page()
        return body

    def today(self):
      (tmy,tmm,tmd, tmh,tmn,tms, tm7,tm8,tm9) = time.gmtime(time.time())
      gmt = (tmy,tmm,tmd, 0,0,0,0,0,0)
      return time.mktime(gmt) - time.timezone

    def chkURL(self, url):
      start_pos = url.find(".", 0)
      if start_pos < 1: return None

      print "url:", url
      service = url[1:start_pos]

      end_pos = url.find("-", start_pos + 1)
      if end_pos < 0: return None
      tmy = int(url[start_pos+1 : end_pos])

      start_pos = end_pos
      end_pos = url.find("-", start_pos + 1)
      if end_pos < 0: return None
      tmm = int(url[start_pos+1 : end_pos])

      start_pos = end_pos
      end_pos = url.find(".", start_pos + 1)
      if end_pos < 0: return None
      tmd = int(url[start_pos+1 : end_pos])

      gmt = (tmy,tmm,tmd, 0,0,0,0,0,0)
      tm = int(time.mktime(gmt) - time.timezone)
      print "service:%s, time:%s"%(service, tm)
      return (service, tm)

    def errorX(self):
      print "errorX"
      return

    def error(self, text):
      self.error = text
      print text

    def gmtime2url(self, service, gmday_from):
      return "%s.%s.html"%(service, time.strftime("%Y-%m-%d", gmday_from))

    def Navigation(self, service, day_from):
      nav = "<P>"
      gmtime = time.gmtime( day_from + 24*3600 )
      
      #service menu
      for s in self.listServices():
        url = self.gmtime2url(s[0], gmtime)
        if s[0] == self.sel_service:
          nav = nav + "<B>%s</B>"%s[0]
        else:
          nav = nav + "<A href=\'%s%s%s\'>%s</A> "%(self.ip, self.scriptUrl, url, s[0])

      #date-day menu
      nav = nav + "</P>\n<P>"
      dayOfWeek = { 0:"Ne", 1:"Po", 2:"Ut", 3:"St", 4:"Ct", 5:"Pa", 6:"So" }

      for day in range(-2, 5):        
        gmtime = time.gmtime( day_from + day*24*3600 )
        date = time.strftime("%Y-%m-%d", gmtime)
        dayCode = int(time.strftime("%w", gmtime))
        date = date + "(" + dayOfWeek[dayCode] + ")"
        url = self.gmtime2url(service, gmtime)
        if day == 1:
          nav = nav + "<B>%s</B>"%date
        else:
          nav = nav + "<A href=\'%s\'>%s</A> "%(url, date)
      return nav + "</P>\n"

    def Page(self):
      body = ""
      date_from = self.sel_date
      service = self.sel_service

      #rozklikavani skript
      body = body + "<script type=\"text/javascript\">\n  function show(id)\n  {\n    var a = document.getElementById(id);\n    a.style.display = (a.style.display == 'block')? 'none' : 'block';\n  }\n</script>\n"

      #calculate date_to
      (dty,dtm,dtd, dth,dtn,dts, dt1,dt2,dt3) = time.gmtime(date_from)
      gmday_from = (dty,dtm,dtd, 0,0,0, 0,0,0)
      day_from = time.mktime(gmday_from)
      date_to = day_from + 24*3600

      #list epg from date to date_to
      body = body + self.Navigation(service, day_from)

      today = self.today()
      url = "http://%s%s%s"%(self.ip, self.url, self.gmtime2url(service, gmday_from))
      if (today > date_from) and (date_from < today + 24*3600):
        body = body + "<BR>" + self.epg(service, date_from - 4*3600, date_to, url)
      else:
        body = body + "<BR>" + self.epg(service, date_from, date_from + 24*3600, url)

      return body

    #search service name
    def serviceName(self, service_id):
      sql = "SELECT service FROM SERVICE WHERE code==%d;"%service_id
      self.cursor.execute(sql)
      return self.cursor.fetchall()[0][0]

    #search short name
    def shortName(self, name_id):
      sql = "SELECT name FROM NAME WHERE id==%d;"%name_id
      self.cursor.execute(sql)
      return self.cursor.fetchall()[0][0]

    #search long text description
    def longName(self, lname_id):
      sql = "SELECT lname FROM LNAME WHERE id==%d;"%lname_id
      self.cursor.execute(sql)
      return self.cursor.fetchall()[0][0]

    #search for conflicts
    def conflicts(self, start, duration, recording, name_id):
      #print "start:%d, duration:%d, recording:%d"%(start, duration, recording)

      conflictInfo = ""
      conflictMark = "&nbsp"

      sql = "SELECT * FROM EPG WHERE name_id!=%d and recording>=1 and ( (start_tm>%d and start_tm<%d) or ((start_tm+duration_tm)>%d and (start_tm+duration_tm)<%d) or ((start_tm)<=%d and (start_tm+duration_tm)>=%d) );"%(name_id, start, start + duration, start, start + duration, start, start + duration)
      self.cursor.execute(sql)
      conflicts = self.cursor.fetchall()
      clen = len(conflicts)
      if clen > 1:
        conflictMark = "!"

        #generate more detail info when remove a program is required
        if clen+1 > self.cardsCount:
          conflictInfo = conflictInfo + "<BLOCKQUOTE>%d conflics found, remove %d recording<BR>\n"%(clen, clen+1-self.cardsCount)
          for item in conflicts:
            (aid, aevent, aservice_id, astart_tm_utc, aduration_tm_utc, aname_id, asname_id, alname_id, arecording) = item
            if aname_id == name_id: continue
            conflictInfo = conflictInfo + self.serviceName(aservice_id) + " \"" + self.shortName(aname_id) + "\"<BR>\n"

          conflictInfo = conflictInfo + "</BLOCKQUOTE>\n"
      return (conflictMark, conflictInfo)


    def epg(self, service, date_from, date_to, url_this):
       date = date_from

       #generate form
       program = "<FORM ACTION=\"%s\" METHOD=POST>\n"%url_this

       #get service_id
       sql = "SELECT * FROM SERVICE WHERE service==\"%s\""%(service)
       self.cursor.execute(sql)
       ret = self.cursor.fetchall()

       if len(ret) == 0:
         self.error( "service \"%s\" not found"%service )
         self.errorX()
         return "error<br>"
       service_id = ret[0][0]

       #list epg
       sql = "SELECT * FROM EPG WHERE service_id==%d and start_tm > %d and start_tm < %d ORDER BY start_tm;"%(service_id, date + time.timezone, date_to)
       self.cursor.execute(sql)
       epg = self.cursor.fetchall()

       for item in epg:
         (id, event, service_id, start_tm_utc, duration_tm_utc, name_id, sname_id, lname_id, recording) = item

         service = self.serviceName(service_id)
         lname = self.longName(lname_id)
         name = self.shortName(name_id)

         start_tm = start_tm_utc - time.timezone
         start_local = time.localtime(start_tm_utc)
         start = time.strftime("%Y-%m-%d %H:%M:%S", start_local)

         duration_tm = duration_tm_utc
         duration_local = time.gmtime(duration_tm)
         duration = time.strftime("%H:%M:%S", duration_local)
           
         (g1,g2,g3, g4,g5,g6, g7,g8,g9) = duration_local
         duration_sec = g4*3600 + g5*60 + g6

         #search for conflicts           
         (conflictMark, conflictInfo) = self.conflicts(start_tm_utc, duration_tm_utc, recording, name_id)

         id = "%s.%d"%(service, start_tm_utc)

         #generate program tag
         if time.time() > (start_tm + duration_sec - time.timezone):
           state = "&nbsp&nbsp"
           if recording>=1: state="*"
           program = program + " [%s] %s %s %s "%(state, conflictMark, start, duration)

         #rozklikavani start
         if len(lname) > 0:
           program = program + "<A HREF='javascript:show(%s);' title='  1'>"%start_tm_utc

           program = program + name + "<br/>\n"
         else:
           state = ""
           if recording >= 1:
             state = "checked"
             program = program + "<input type=\"hidden\" name=\"epgpreset\" value=\"%s\">\n"%(id)
           program = program + "<input type=\"checkbox\" %s name=\"epgset\" value=\"%s\"/>%s %s %s "%(state, id, conflictMark, start, duration)

           #rozklikavani start
           if len(lname) > 0:
             program = program + "<A HREF='javascript:show(%s);' title='  1'>"%start_tm_utc
           program = program + name + "<br/>\n"

         #podrobne info + konflikty + rozklikavani konec
         if len(lname) > 0:
           program = program + "</A><DIV STYLE='display: none;' ID='%s' CLASS=''>"%start_tm_utc + lname + "</DIV>" + "\n"

         # add conflict info when recording
         if recording >= 1:
           program = program + conflictInfo + "\n"

       program = program + "</SELECT><INPUT TYPE=SUBMIT VALUE=Send></FORM>"
       return program

    def errorHandler(self):
      print 'Caught: sys.exc_type =', sys.exc_type, 'sys.exc_value =', sys.exc_value
      print 'sys.exc_traceback =', sys.exc_traceback
      print sys.exc_info()
      print "--------"

      maxTBlevel=5
      cla, exc, trbk = sys.exc_info()
      excName = cla.__name__
      try:
        excArgs = exc.__dict__["args"]
      except KeyError:
        excArgs = "<no args>"
      excTb = traceback.format_tb(trbk, maxTBlevel)
      print (excName, excArgs, excTb)

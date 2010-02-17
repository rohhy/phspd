#Ptyhon Http Secure Path DB
#!/usr/bin/python
import sqlite3
import os, shutil, time  #db backup
#import exception


class DBError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


class phspdb:
  def __init__(self):

    #consts
    self.HTTPS_NONE = 0
    self.HTTPS_DEFAULT_NONE = 1
    self.HTTPS_DEFAULT_RO = 2
    self.HTTPS_DEFAULT_WO = 3
    self.HTTPS_DEFAULT_RW = 4

    self.dbpath = 'phsp.db'
    self.connection = sqlite3.connect(self.dbpath)
    self.cursor = self.connection.cursor()
    return  

  def __del__(self):
    self.Close()

  def Close(self):
    self.connection.commit()
    self.connection.close()
    return 

  def CreateTable(self, tableName, tableParams):
    sql = "CREATE TABLE %s(%s)"%(tableName, tableParams)
    self.cursor.execute(sql)
    self.connection.commit()
    return
 
  # Tables() - table details: tables[ name, cols[ (colName, colType) ] ]
  def Tables(self):
    sql = "SELECT tbl_name, sql FROM sqlite_master WHERE type='table'"
    self.cursor.execute(sql)
    res = self.cursor.fetchall()

    tables = []
    if len(res) > 0:
      for table in res:
        tableName = table[0]

        cmd = table[1]
        cols = cmd[cmd.find("(") +1 : cmd.rfind(")")].split(',')

        if len(cols) > 0:

          columns = []
          for column in cols:

            separator = column.find(" ")
            if separator == 0:
              column = column[1:]
              separator = column.find(" ")

            colName = column[0:separator]
            colType = column[separator+1:]
            columns.append( (colName, colType) )

          tables.append( (tableName, columns) )

    return tables

  def Init(self):
    #backup old db
    if os.path.exists(self.dbpath) and os.path.getsize(self.dbpath) > 0:
      nameTime = time.strftime("%y%m%d%H%M%S", time.localtime(time.time()))
      shutil.copyfile(self.dbpath, "%s.%s"%(self.dbpath, nameTime))

    #remove all tables
    res = self.Tables()
    if len(res) > 0:
      for table in res:
        print "remove table %s"%table[1]
        sql = "DROP TABLE %s"%table[1]
        self.cursor.execute(sql)

    #create db
    self.CreateTable("access", "id INTEGER PRIMARY KEY, user INTEGER, https INTEGER, rights INTEGER")
    self.CreateTable("https", "id INTEGER PRIMARY KEY, script_path VARCHAR(128), url_ext VARCHAR(128), default_access INTEGER")
    self.CreateTable("user", "id INTEGER PRIMARY KEY, cert_path VARCHAR(128)")

  def userRaw(self, certPath):
    sql = "SELECT * FROM user WHERE cert_path = \"%s\""%certPath
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def userName(self, userId):
    sql = "SELECT * FROM user WHERE id = %d"%userId
    self.cursor.execute(sql)
    res = self.cursor.fetchall()
    if len(res) > 0: return res[0][1]
    msg = "User id:%d not found"%userId
    raise Exception(msg)

  #deprecated, use userId
  def user(self, certPath):
    return self.userIdByCert(certPath)

  def userIdByCert(self, certPath):
    userName = self.CertPath2UserName(certPath)
    res = self.userRaw(userName)
    if len(res) == 0:
      msg = "no user, cert path: %s"%certPath
      raise DBError(msg)
    return res[0][0]

  def httpsRaw(self, urlExt):
    sql = "SELECT * FROM https WHERE url_ext = \"%s\""%urlExt
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def https(self, urlExt):
    res = self.httpsRaw(urlExt)
    if len(res) == 0:
      msg = "no https, url extension: %s"%urlExt
      raise DBError(msg)
    return res[0]

  def httpsById(self, httpsId):
    sql = "SELECT * FROM https WHERE id = %d"%httpsId
    self.cursor.execute(sql)
    res = self.cursor.fetchall()
    if len(res) == 0:
      msg = "no https, url extension: %s"%httpsId
      raise DBError(msg)
    return res[0]

  def accessRaw(self, httpsId, userId):
    sql = "SELECT * FROM access WHERE user=%d and https=%d"%(userId, httpsId)
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def accesses(self):
    sql = "SELECT * FROM access"
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def access(self, httpsId, userId):
    res = self.accessRaw(httpsId, userId)
    if len(res) > 0: return res[0]
    return 0   #no permissions by default

  def accessHttps(self, urlExt):
    sql = "SELECT * FROM access WHERE https=%s"%urlExt
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def accessUser(self, userName):
    sql = "SELECT * FROM access WHERE user=\"%s\""%userName
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def addUser(self, certPath):
    res = self.userRaw(certPath)
    if len(res) > 0:
      (id, certDB) = res[0]
      sql = "UPDATE user SET cert_path = \"%s\" WHERE id=%d"%(certPath, id)
    else:
      sql = "INSERT INTO user VALUES(NULL,\"%s\")"%(certPath)
    self.cursor.execute(sql)
    self.connection.commit()

  def addHttps(self, scriptPath, urlExt, defaultAccess):
    res = self.httpsRaw(urlExt)
    if len(res) > 0:
      sql = "UPDATE https SET script_path=\"%s\", url_ext=\"%s\", default_access=%d WHERE id=%d"%(scriptPath, urlExt, defaultAccess, res[0][0])
    else:
      sql = "INSERT INTO https VALUES(NULL,\"%s\",\"%s\",%d)" \
              %(scriptPath, urlExt, defaultAccess)
    print "sql", sql
    self.cursor.execute(sql)
    self.connection.commit()

  def addAccess(self, httpsId, userId, rights):
    res = self.accessRaw(httpsId, userId)
    if len(res) > 0:
      id = res[0][0]
      sql = "UPDATE access SET https=%d, rights=%d WHERE id=%d;"%(httpsId, rights, id)
    else:
      sql = "INSERT INTO access (user, https, rights) VALUES (%d,%d,%d)"%(userId, httpsId, rights)
    print sql
    self.cursor.execute(sql)
    self.connection.commit()

  def rmAccess(self, httpsId, userId):
    if self.access(httpsId, userId) == self.HTTPS_DEFAULT_NONE: return
    sql = "DELETE FROM access WHERE https=%s AND user=%s"%(httpsId, userId)
    self.cursor.execute(sql)
    self.connection.commit()

  def rmHttps(self, urlExt):
    if len(https(urlExt)) == 0: return
    sql = "DELETE FROM https WHERE url_ext=%s"%(urlExt)
    self.cursor.execute(sql)
    self.connection.commit()

  def rmUser(self, certPath):
    if len(user(certPath)) == 0: return
    sql = "DELETE FROM https WHERE cert_path=%s"%(certPath)
    self.cursor.execute(sql)
    self.connection.commit()

  def UserName2CertPath(self, userName):
    return "%scert.pem"%userName
  
  def CertPath2UserName(self, certPath):
    return certPath[:-8]

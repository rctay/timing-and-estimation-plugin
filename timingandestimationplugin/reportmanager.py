from trac.core import *


class CustomReportManager:
  """A Class to manage custom reports"""
  version = 1
  name = "custom_report_manager_version"
  env = None
  log = None
  
  def __init__(self, env, log):
    self.env = env
    self.log = log
    self.upgrade()
  
  def upgrade(self):  
    # Check to see what version we have
    db = self.env.get_db_cnx()
    cursor = db.cursor()
    cursor.execute("SELECT value FROM system WHERE name=%s", (self.name,))
    try:
      version = int(cursor.fetchone()[0])
    except:
      version = 0
      cursor.execute("INSERT INTO system (name,value) VALUES(%s,%s)",
                     (self.name, version))
        
    if version > self.version:
      raise TracError("Fatal Error: You appear to be running two plugins with conflicting versions "
                      "of the CustomReportManager class. Please ensure that '%s' is updated to "
                      "version %s of the file reportmanager.py (currently using version %s)."
                      % (__name__, str(version), str(self.version)))
    
    # Do the staged updates
    try:
      if version < 1:
        cursor.execute("CREATE TABLE custom_report ("
                       "id         INTEGER,"
                       "uuid       VARCHAR(64),"
                       "maingroup  VARCHAR(255),"
                       "subgroup   VARCHAR(255),"
                       "version    INTEGER,"
                       "ordering   INTEGER)")
      
      #if version < 2:
      #  cursor.execute("...")
    
      # Updates complete, set the version
      cursor.execute("UPDATE system SET value=%s WHERE name=%s", 
                     (self.version, self.name))
      db.commit()
      db.close()
    
    except Exception, e:
      self.log.error("CustomReportManager Exception: %s" % (e,));
      db.rollback()
  
  def add_report(self, title, author, description, query, uuid, version, maingroup, subgroup=""):
    # First check to see if we can load an existing version of this report
    db = self.env.get_db_cnx()
    cursor = db.cursor()
    try:
      cursor.execute("SELECT id, version FROM custom_report "
                     "WHERE uuid=%s", (uuid,))
      (id, currentversion) = cursor.fetchone()          
    except:
      id = None
      currentversion = 0
    
    try:
      if not id:
        cursor.execute("SELECT MAX(id) FROM report")
        next_id = int(cursor.fetchone()[0]) + 1
        self.log.debug("Inserting new report with uuid '%s'" % (uuid,));

        # Get the ordering of any current reports in this group/subgroup.
        try:
          cursor.execute("SELECT MAX(ordering) FROM custom_report "
                         "WHERE maingroup=%s AND subgroup=%s", (maingroup, subgroup))
          ordering = int(cursor.fetchone()[0]) + 1
        except:
          ordering = 0
        
        cursor.execute("INSERT INTO report (id, title, author, description, query) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (next_id, title, author, description, query))
        cursor.execute("INSERT INTO custom_report (id, uuid, maingroup, subgroup, version, ordering) "
                       "VALUES (%s, %s, %s, %s, %s, %s)",
                       (next_id, uuid, maingroup, subgroup, version, ordering))
        db.commit()
        db.close()
        return True
      if currentversion < version:
        self.log.debug("Updating report with uuid '%s' to version %s" % (uuid,version));
        cursor.execute("UPDATE report SET title=%s, author=%s, description=%s, query=%s "
                       "WHERE id=%s", (title, author, description, query, id))
        cursor.execute("UPDATE custom_report SET version=%s, maingroup=%s, subgroup=%s "
                       "WHERE id=%s", (version, maingroup, subgroup, id))
        db.commit()
        db.close()
        return True
    except Exception, e:
      self.log.error("CustomReportManager Exception: %s" % (e,));
      db.rollback()
    
    return False
  
  def get_report_by_uuid(self, uuid):
    db = self.env.get_db_cnx()
    cursor = db.cursor()
    rv = None
    try:
      cursor.execute("SELECT report.id,report.title FROM custom_report "
                     "LEFT JOIN report ON custom_report.id=report.id "
                     "WHERE custom_report.uuid=%s", (uuid,))
      row = cursor.fetchone()
      rv = (row[0], row[1])
    except:
      pass
    
    return rv
  
  def get_reports_by_group(self, group):
    db = self.env.get_db_cnx()
    cursor = db.cursor()
    rv = {}
    try:
      cursor.execute("SELECT custom_report.subgroup,report.id,report.title "
                     "FROM custom_report "
                     "LEFT JOIN report ON custom_report.id=report.id "
                     "WHERE custom_report.maingroup=%s "
                     "ORDER BY custom_report.subgroup,custom_report.ordering", (group,))
      for subgroup,id,title in cursor:
        if not rv.has_key(subgroup):
          rv[subgroup] = { "title": subgroup,
                           "reports": [] }
        rv[subgroup]["reports"].append( { "id": int(id), "title": title } )
    except:
      pass
    
    return rv


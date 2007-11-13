from trac.core import *
import dbhelper


class CustomReportManager:
  """A Class to manage custom reports"""
  version = 1
  name = "custom_report_manager_version"
  env = None
  log = None
  TimingAndEstimationKey = "Timing and Estimation Plugin"
  
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

  def get_report_id_and_version (self, uuid):
    sql = "SELECT id, version FROM custom_report " \
          "WHERE uuid=%s"
    tpl = dbhelper.get_first_row(self.env.get_db_cnx(), sql, uuid)
    return tpl or (None, 0)
    
  def get_new_report_id (self):
    return dbhelper.get_scalar(self.env.get_db_cnx(),"SELECT MAX(id) FROM report")

  def get_max_ordering(self, maingroup, subgroup):
    return dbhelper.get_scalar(self.env.get_db_cnx(),
      "SELECT MAX(ordering) FROM custom_report WHERE maingroup=%s AND subgroup=%s",
      0, maingroup, subgroup) or 0
  
  def _insert_report (self, next_id, title, author, description, query,
                      uuid, maingroup, subgroup, version, ordering):
    self.log.debug("Inserting new report '%s' with uuid '%s'" % (title,uuid))
    dbhelper.execute(self.env.get_db_cnx(),
      "INSERT INTO report (id, title, author, description, query) " \
      "VALUES (%s, %s, %s, %s, %s)", next_id, title, author, description, query)
    dbhelper.execute(self.env.get_db_cnx(),
      "INSERT INTO custom_report (id, uuid, maingroup, subgroup, version, ordering) "\
      "VALUES (%s, %s, %s, %s, %s, %s)", next_id, uuid, maingroup, subgroup, version, ordering)

  def _update_report (self, id, title, author, description, query,
                      maingroup, subgroup, version):
    self.log.debug("Updating report '%s' with uuid '%s' to version %s" % (title, uuid, version))
    dbhelper.execute(self.env.get_db_cnx(),
      "UPDATE report SET title=%s, author=%s, description=%s, query=%s " \
      "WHERE id=%s", title, author, description, query, id)
    dbhelper.execute(self.env.get_db_cnx(),
      "UPDATE custom_report SET version=%s, maingroup=%s, subgroup=%s "
      "WHERE id=%s", version, maingroup, subgroup, id)
                     
  def add_report(self, title, author, description, query, uuid, version,
                 maingroup, subgroup="", force=False):
    """ If force is set, we ignore the version and re set the value anyway
    """
    # First check to see if we can load an existing version of this report
    (id, currentversion) = self.get_report_id_and_version(uuid)
    try:
      if not id:
        next_id = self.get_new_report_id()
        ordering = self.get_max_ordering(maingroup, subgroup) + 1
        self._insert_report(next_id, title, author, description, query,
                      uuid, maingroup, subgroup, version, ordering)
        return True
      if currentversion < version or force:
        self._update_report(id, title, author, description, query,
                            maingroup, subgroup, version)
        return True
    except Exception, e:
      self.log.error("CustomReportManager Exception: %s" % (e,));
    return False
  
  def get_report_by_uuid(self, uuid):
    sql = "SELECT report.id,report.title FROM custom_report "\
          "LEFT JOIN report ON custom_report.id=report.id "\
          "WHERE custom_report.uuid=%s"
    return dbhelper.get_first_row(self.env.get_db_cnx(),sql,uuid)
  
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


from trac.core import *



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
    tpl = self.get_first_row(sql, uuid)
    return tpl or (None, 0)
    
  def get_new_report_id (self):
    """find the next available report id """
    rtn = self.get_scalar("SELECT MAX(id) FROM report")
    return (rtn and rtn+1) or 1
    
  def get_max_ordering(self, maingroup, subgroup):
    """ Find the maximum ordering value used for this group of the custom_report table"""
    return self.get_scalar("SELECT MAX(ordering) FROM custom_report WHERE maingroup=%s AND subgroup=%s",
                           0, maingroup, subgroup) or 0
  
  def _insert_report (self, next_id, title, author, description, query,
                      uuid, maingroup, subgroup, version, ordering):
    """ Adds a row the custom_report_table """
    self.log.debug("Inserting new report '%s' with uuid '%s'" % (title,uuid))
    self.execute_in_trans(("INSERT INTO report (id, title, author, description, query) " \
                           "VALUES (%s, %s, %s, %s, %s)",
                           (next_id, title, author, description, query)),
                          ("INSERT INTO custom_report (id, uuid, maingroup, subgroup, version, ordering) " \
                           "VALUES (%s, %s, %s, %s, %s, %s)",
                           (next_id, uuid, maingroup, subgroup, version, ordering)))
    self.log.debug("Attempting to increment sequence")
    try:
      self.execute_in_trans(("SELECT nextval('report_id_seq');",[]));
      self.log.debug("Sequence updated");
    except:
      self.log.debug("Sequence failed to update, perhaps you are not running postgres?");

  def _update_report (self, id, title, author, description, query,
                      maingroup, subgroup, version):
    """Updates a report and its row in the custom_report table """
    self.log.debug("Updating report '%s' with to version %s" % (title, version))
    self.execute_in_trans(("UPDATE report SET title=%s, author=%s, description=%s, query=%s " \
                           "WHERE id=%s", (title, author, description, query, id)),
                          ("UPDATE custom_report SET version=%s, maingroup=%s, subgroup=%s "
                           "WHERE id=%s", (version, maingroup, subgroup, id)))
    
  def add_report(self, title, author, description, query, uuid, version,
                 maingroup, subgroup="", force=False):
    """
    We add/update a report to the system. We will not overwrite unchanged versions
    unless force is set.
    """
    # First check to see if we can load an existing version of this report
    (id, currentversion) = self.get_report_id_and_version(uuid)
    self.log.debug("add_report %s (ver:%s) | id: %s currentversion: %s" % (uuid , version, id, currentversion))
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
      self.log.error("CustomReportManager.add_report Exception: %s, %s" % (e,(title, author, uuid, version,
                 maingroup, subgroup, force)));
    self.log.debug("report %s not upgraded (a better version already exists)" % uuid)
    return False
  
  def get_report_by_uuid(self, uuid):
    sql = "SELECT report.id,report.title FROM custom_report "\
          "LEFT JOIN report ON custom_report.id=report.id "\
          "WHERE custom_report.uuid=%s"
    return self.get_first_row(sql,uuid)
  
  def get_reports_by_group(self, group):
    """Gets all of the reports for a given group"""
    db = self.env.get_db_cnx()
    cursor = db.cursor()
    rv = {}
    try:
      cursor.execute("SELECT custom_report.subgroup,report.id,report.title, custom_report.version, custom_report.uuid "
                     "FROM custom_report "
                     "LEFT JOIN report ON custom_report.id=report.id "
                     "WHERE custom_report.maingroup=%s "
                     "ORDER BY custom_report.subgroup,custom_report.ordering", (group,))
      for subgroup, id, title, version, uuid in cursor:
        if not rv.has_key(subgroup):
          rv[subgroup] = { "title": subgroup,
                           "reports": [] }
        rv[subgroup]["reports"].append( { "id": int(id), "title": title, "version":version, "uuid":uuid } )
    except:
      pass
    return rv

  # similar functions are found in dbhelper, but this file should be fairly
  # stand alone so that it can be copied and pasted around
  def get_first_row(self, sql,*params):
    """ Returns the first row of the query results as a tuple of values (or None)"""
    db = self.env.get_db_cnx()
    cur = db.cursor()
    data = None;
    try:
      cur.execute(sql, params)
      data = cur.fetchone();
      db.commit();
    except Exception, e:
      self.log.error('There was a problem executing sql:%s \n \
      with parameters:%s\nException:%s'%(sql, params, e));
      db.rollback()
    try:
      db.close()
    except:
      pass
    return data;

  def get_scalar(self, sql, col=0, *params):
    """ Gets a single value (in the specified column) from the result set of the query"""
    data = self.get_first_row(sql, *params);
    if data:
      return data[col]
    else:
      return None;

  def execute_in_trans(self, *args):
    success = True
    db = self.env.get_db_cnx()
    cur = db.cursor()
    try:
      for sql, params in args:
        cur.execute(sql, params)
      db.commit()
    except Exception, e:
      self.log.error('There was a problem executing sql:%s \n \
      with parameters:%s\nException:%s'%(sql, params, e));
      db.rollback();
      success = False
    try:
      db.close()
    except:
      pass
    return success

    

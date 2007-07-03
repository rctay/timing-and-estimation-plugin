import re
import dbhelper
import time
from ticket_daemon import *
from usermanual import *
from reports import all_reports
from trac.log import logger_factory
from trac.ticket import ITicketChangeListener, Ticket
from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor, PermissionSystem
from webui import * 
from ticket_webui import *
from query_webui import *

## report columns
## id|author|title|query|description
   
class TimeTrackingSetupParticipant(Component):
    """ This is the config that must be there for this plugin to work:
        
        [ticket-custom]
        totalhours = text
        totalhours.value = 0
        totalhours.label = Total Hours

        billable = checkbox
        billable.value = 1
        billable.label = Is this billable?

        hours = text
        hours.value = 0
        hours.label = Hours to Add
        
        estimatedhours = text
        estimatedhours.value = 0
        estimatedhours.label = Estimated Hours?
        
        """
    implements(IEnvironmentSetupParticipant)
    
    """Extension point interface for components that need to participate in the
    creation and upgrading of Trac environments, for example to create
    additional database tables."""
    def __init__(self):
        sql = "SELECT id, title FROM report ORDER BY ID"
        dbhelper.mylog = self.log
        self.reportmap = dbhelper.get_all(self.env.get_db_cnx(), sql)[1]
        
    def environment_created(self):
        """Called when a new Trac environment is created."""
        if self.environment_needs_upgrade(None):
            self.upgrade_environment(None)
            
    def db_needs_upgrade(self):
        bill_date = dbhelper.db_table_exists(self.env.get_db_cnx(), 'bill_date');
        report_version = dbhelper.db_table_exists(self.env.get_db_cnx(), 'report_version');
        val =  dbhelper.db_needs_upgrade(self.env.get_db_cnx())
        return val or not bill_date or not report_version
        
    def db_do_upgrade(self):
        bill_date = dbhelper.db_table_exists(self.env.get_db_cnx(), 'bill_date');
        report_version = dbhelper.db_table_exists(self.env.get_db_cnx(), 'report_version');
        if not bill_date:
            print "Creating bill_date table"
            sql = """
            CREATE TABLE bill_date (
            time integer,
            set_when integer,
            str_value text
            );
            """
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)
            
            
        if not report_version:
            print "Creating report_version table"
            sql = """
            CREATE TABLE report_version (
            report integer,
            version integer,
            UNIQUE (report, version)
            );
            """
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)
        dbhelper.migrate_up_to_version(self.env.get_db_cnx, dbhelper)
        dbhelper.set_plugin_db_version(self.env.get_db_cnx)
    
    def reports_need_upgrade(self):
        bit = False
        report_version = dbhelper.db_table_exists(self.env.get_db_cnx(), 'report_version');
        if not report_version:
            return True
        
        #make versions hash
        try:
            _versions = dbhelper.get_result_set(self.env.get_db_cnx(),"""
               SELECT report as id, version, r.title as title
               FROM report_version
               JOIN report r ON r.Id = report_version.report
               WHERE tags LIKE '%T&E%' """)
        except Exception:
            return True;
        versions = {}

        if _versions.rows == None:
            return True

        for (id, version, title) in _versions.rows:
            versions[title] = (id, version)

            
        for report_group in all_reports:
            rlist = report_group["reports"]
            for report in rlist:
                title = report["title"]
                new_version = report["version"]
                #the report map is a list of (id, name) tuples for the reports
                # here we want to see if our report is in the list
                idx = [i for i in range(0, len(self.reportmap)) if self.reportmap[i][1] == title]
                if not idx:
                    self.log.warning("Report '%s' needs to be added" % title)
                    bit = True;
                else:
                    # If we had a report make sure its at the correct version
                    if versions.has_key(title):
                        (id, ver) = versions[title]
                    else:
                        ver = 0
                    if ver < new_version:
                        bit = True
        return bit
                
    def do_reports_upgrade(self):
        self.log.debug( "Beginning Reports Upgrade");
        #make version hash
        _versions = dbhelper.get_result_set(self.env.get_db_cnx(),
                                           """
                                           SELECT report as id, version, r.title as title
                                           FROM report_version
                                           JOIN report r ON r.Id = report_version.report
                                           WHERE tags LIKE '%T&E%'
                                           """)
        versions = {}
        if _versions and _versions.rows:
            for (id, version, title) in _versions.rows:
                versions[title] = (id, version)
            
        biggestId = dbhelper.get_scalar(self.env.get_db_cnx(),
                                        "SELECT ID FROM report ORDER BY ID DESC LIMIT 1")
        def insert_report_version(id, ver, tag):
            sql = "DELETE FROM report_version WHERE report = %s;"
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql, id  )
            sql = """
            INSERT INTO report_version (report, version, tags)
            VALUES (%s, %s, %s);"""
            # print "about to insert report_version"
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql, id, ver, tag )
            # print "inserted report_version"
            
        for report_group in all_reports:
            rlist = report_group["reports"]
            group_title = report_group["title"]
            tag = "T&E %s" % group_title
            for report in rlist:
                title = report["title"]
                new_version = report["version"]
                report_id = [rid
                             for (rid, map_title) in self.reportmap
                             if map_title == title]
                if not report_id:
                    bit = True; 
                    sql = """INSERT INTO report (id,author,title,query,description) 
                             VALUES (%s,'Timing and Estimation Plugin',%s,%s,'') """
                    biggestId += 1
                    dbhelper.execute_non_query(self.env.get_db_cnx(), sql,
                                               biggestId, title, report["sql"])
                    insert_report_version(biggestId, new_version, tag)

                    report["reportnumber"] = biggestId
                    self.reportmap.extend([(biggestId,title)])
                else:
                    report_id = report_id[0]
                    report["reportnumber"] = report_id
                     # If we had a report make sure its at the correct version
                    if versions.has_key(title):
                        ( _ , ver) = versions[title]
                    else:
                        ver = 0
                    if not ver:
                        sql = """
                        UPDATE report
                        SET query=%s 
                        WHERE id = %s """
                        print "updating report: %s" % title
                        dbhelper.execute_non_query(self.env.get_db_cnx(), sql,
                                                   report["sql"], report_id )
                        insert_report_version( report_id, new_version, tag )
                    elif ver < new_version:
                        sql = """
                        UPDATE report
                        SET query=%s 
                        WHERE id = %s """
                        print "updating report to new version: %s" % title
                        dbhelper.execute_non_query(self.env.get_db_cnx(), sql,
                                                   report["sql"], report_id )
                        
                        sql = """
                        UPDATE report_version
                        SET version = %s, tags = %s
                        
                        WHERE report = %s
                        """
                        dbhelper.execute_non_query(self.env.get_db_cnx(), sql, new_version, tag, report_id)
                        
    def ticket_fields_need_upgrade(self):
        ticket_custom = "ticket-custom"
        return not ( self.config.get( ticket_custom, "totalhours" ) and \
                     self.config.get( ticket_custom, "billable" ) and \
                     (self.config.get( ticket_custom, "billable" ) == "checkbox") and \
                     self.config.get( ticket_custom, "hours" ) and \
                     (not self.config.get( ticket_custom, "lastbilldate" )) and \
                     self.config.get( ticket_custom, "totalhours.order") and \
                     self.config.get( ticket_custom, "hours.order") and \
                     self.config.get( ticket_custom, "estimatedhours.order") and \
                     self.config.get( ticket_custom, "billable.order") and \
                     self.config.get( ticket_custom, "estimatedhours"))
    
    def do_ticket_field_upgrade(self):
        ticket_custom = "ticket-custom"
        
        self.config.set(ticket_custom,"totalhours", "text")
        if not self.config.get( ticket_custom, "totalhours.order") :
            self.config.set(ticket_custom,"totalhours.order", "4")
        self.config.set(ticket_custom,"totalhours.value", "0")
        self.config.set(ticket_custom,"totalhours.label", "Total Hours")                

        self.config.set(ticket_custom,"billable", "checkbox")
        self.config.set(ticket_custom,"billable.value", "1")
        if not self.config.get( ticket_custom, "billable.order") :
            self.config.set(ticket_custom,"billable.order", "3")
        self.config.set(ticket_custom,"billable.label", "Billable?")
            
        self.config.set(ticket_custom,"hours", "text")
        self.config.set(ticket_custom,"hours.value", "0")
        if not self.config.get( ticket_custom, "hours.order") :
            self.config.set(ticket_custom,"hours.order", "2")
        self.config.set(ticket_custom,"hours.label", "Add Hours to Ticket")
            
        self.config.set(ticket_custom,"estimatedhours", "text")
        self.config.set(ticket_custom,"estimatedhours.value", "0")
        if not self.config.get( ticket_custom, "estimatedhours.order") :
            self.config.set(ticket_custom,"estimatedhours.order", "1")
        self.config.set(ticket_custom,"estimatedhours.label", "Estimated Number of Hours")

        self.config.save();

    def needs_user_man(self):
        maxversion = dbhelper.get_scalar(self.env.get_db_cnx(),
                                         "SELECT MAX(version) FROM wiki WHERE name like %s", 0,
                                         user_manual_wiki_title)
        if (not maxversion) or maxversion < user_manual_version:
            return True
        return False

    def do_user_man_update(self):

        when = int(time.time())
        sql = """
        INSERT INTO wiki (name,version,time,author,ipnr,text,comment,readonly)
        VALUES ( %s, %s, %s, 'Timing and Estimation Plugin', '127.0.0.1', %s,'',0)
        """
        dbhelper.execute_non_query(self.env.get_db_cnx(),sql,
                                   user_manual_wiki_title,
                                   user_manual_version,
                                   when,
                                   user_manual_content)
            
        
    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.
        
        Should return `True` if this participant needs an upgrade to be
        performed, `False` otherwise.

        """
        return (self.db_needs_upgrade()) or \
               (self.ticket_fields_need_upgrade()) or \
               (self.reports_need_upgrade()) or \
               (self.needs_user_man()) 
            
    def upgrade_environment(self, db):
        """Actually perform an environment upgrade.
        
        Implementations of this method should not commit any database
        transactions. This is done implicitly after all participants have
        performed the upgrades they need without an error being raised.
        """
        def p(s):
            print s
            return True
        print "Timing and Estimation needs an upgrade"
        if self.db_needs_upgrade():
            p("Upgrading Database")
            self.db_do_upgrade()
        if self.ticket_fields_need_upgrade():
            p("Upgrading fields")
            self.do_ticket_field_upgrade()
        if self.reports_need_upgrade():
            p("Upgrading reports")
            self.do_reports_upgrade()
        if self.needs_user_man():
            p("Upgrading usermanual")
            self.do_user_man_update()
        print "Done Upgrading"


        



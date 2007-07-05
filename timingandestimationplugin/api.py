import re
import dbhelper
import time
from ticket_daemon import *
from usermanual import *
from trac.log import logger_factory
from trac.ticket import ITicketChangeListener, Ticket
from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor, PermissionSystem
from webui import * 
from ticket_webui import *
from query_webui import *
from reportmanager import CustomReportManager


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
    db_version_key = None
    db_version = None
    db_installed_version = None
    
    """Extension point interface for components that need to participate in the
    creation and upgrading of Trac environments, for example to create
    additional database tables."""
    def __init__(self):
        # Setup logging
        dbhelper.mylog = self.log
        self.db_version_key = 'TimingAndEstimationPlugin_Db_Version'
        self.db_version = 5
        self.db_installed_version = None

        # Initialise database schema version tracking.
        db = self.env.get_db_cnx()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM system WHERE name=%s", (self.db_version_key,))
        try:
            self.db_installed_version = int(cursor.fetchone()[0])
        except:
            self.db_installed_version = 0
            cursor.execute("INSERT INTO system (name,value) VALUES(%s,%s)",
                           (self.db_version_key, self.db_installed_version))
            db.commit()
            db.close()
            print "Done"

    def environment_created(self):
        """Called when a new Trac environment is created."""
        if self.environment_needs_upgrade(None):
            self.upgrade_environment(None)
            

    def system_needs_upgrade(self):
        return self.db_installed_version < self.db_version
        
    def do_db_upgrade(self):
        # Legacy support hack (supports upgrades from 0.1.6 to 0.1.7)
        if self.db_installed_version == 0:
            bill_date = dbhelper.db_table_exists(self.env.get_db_cnx(), 'bill_date');
            report_version = dbhelper.db_table_exists(self.env.get_db_cnx(), 'report_version');
            if bill_date and report_version:
                self.db_installed_version = 1
        # End Legacy support hack

        
        if self.db_installed_version < 1:
            print "Creating bill_date table"
            sql = """
            CREATE TABLE bill_date (
            time integer,
            set_when integer,
            str_value text
            );
            """
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)
            
            print "Creating report_version table"
            sql = """
            CREATE TABLE report_version (
            report integer,
            version integer,
            UNIQUE (report, version)
            );
            """
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)

        if self.db_installed_version < 4:
            print "Upgrading report_version table to v4"
            sql ="""
            ALTER TABLE report_version ADD COLUMN tags varchar(1024) null;
            """
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)

        if self.db_installed_version < 5:
            # In this version we convert to using reportmanager.py
            # The easiest migration path is to remove all the reports!!
            # They will be added back in later but all custom reports will be lost (deleted)
            print "Dropping report_version table"
            sql = "DELETE FROM report " \
                  "WHERE author=%s AND id IN (SELECT report FROM report_version)"
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql, 'Timing and Estimation Plugin')

            sql = "DROP TABLE report_version"
            dbhelper.execute_non_query(self.env.get_db_cnx(), sql)

                
        # This statement block always goes at the end this method
        sql = "UPDATE system SET value=%s WHERE name=%s"
        dbhelper.execute_non_query(self.env.get_db_cnx(),
                                   sql, self.db_version, self.db_version_key)
        self.db_installed_version = self.db_version
    

    def do_reports_upgrade(self):
        self.log.debug( "Beginning Reports Upgrade");
        mgr = CustomReportManager(self.env, self.log)
        r = __import__("reports", globals(), locals(), ["all_reports"])

        for report_group in r.all_reports:
            rlist = report_group["reports"]
            group_title = report_group["title"]
            for report in rlist:
                title = report["title"]
                new_version = report["version"]
                mgr.add_report(report["title"], "Timing and Estimation Plugin", \
                               "", report["sql"], \
                               report["uuid"], report["version"],
                               "Timing and Estimation Plugin",
                               group_title)

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
        return (self.system_needs_upgrade()) or \
               (self.ticket_fields_need_upgrade()) or \
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
        p("Upgrading Database")
        self.do_db_upgrade()
        p("Upgrading reports")
        self.do_reports_upgrade()

        if self.ticket_fields_need_upgrade():
            p("Upgrading fields")
            self.do_ticket_field_upgrade()
        if self.needs_user_man():
            p("Upgrading usermanual")
            self.do_user_man_update()
        print "Done Upgrading"


        




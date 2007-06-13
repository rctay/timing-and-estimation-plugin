import re
import time
import datetime
import dbhelper
from usermanual import * 
from reports import all_reports
from trac.log import logger_factory
from trac.core import *
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.chrome import add_stylesheet, add_script, \
     INavigationContributor, ITemplateProvider
from trac.web.href import Href



class TimingEstimationAndBillingPage(Component):
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    #CACHING THIS WAS CAUSING PROBLEMS ON A GLOBAL INSTALL
    def get_copy_report_hash_for_render(self, req):
        new_reports = []
        sql = "SELECT id, title FROM report ORDER BY ID"
        self.reportmap = dbhelper.get_all(self.env.get_db_cnx(), sql)[1]
        
        for report_group in all_reports:
            new_group = { "title" : report_group["title"] }
            reports_list = report_group["reports"]
            new_reports_list = []
            for report in reports_list:
                title = report["title"]
                #find the report id for the name
                try:
                    reportid = [r_id
                                for (r_id, r_name) in self.reportmap
                                if r_name == title][0]
                
                    new_report = {"title" : title,
                                  "reportnumber" : reportid,
                                  "href" : "%s/%s" % (req.href.report(), reportid)}
                    new_reports_list.extend([ new_report ])
                except:
                    pass
            new_group["reports"] = new_reports_list
            new_reports.extend([new_group])
        return new_reports
            
    def __init__(self):
        pass

    def set_bill_date(self, username="Timing and Estimation Plugin",  when=0):
        now = time.time()
        if not when:
            when = now
        when = int(when)
        now = int(now)
        dtwhen = datetime.datetime.fromtimestamp(when);
        strwhen = "%s/%s/%s %#02d:%#02d:%#02d" % \
                (dtwhen.month, dtwhen.day,dtwhen.year, dtwhen.hour,dtwhen.minute, dtwhen.second)
        sql = """
        INSERT INTO bill_date (time, set_when, str_value)
        VALUES (%s, %s, %s)
        """
        dbhelper.execute_non_query(self.env.get_db_cnx(), sql, when, now, strwhen)
        
        
            
    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        if re.search('/Billing', req.path_info):
            return "Billing"
        else:
            return ""

    def get_navigation_items(self, req):
        url = req.href.Billing()
        if req.perm.has_permission("REPORT_VIEW"):
            yield 'mainnav', "Billing", \
                  Markup('<a href="%s">%s</a>' % \
                         (url , "Management"))

    # IRequestHandler methods
    def set_request_billing_dates(self, req):
        billing_dates = []
        billing_time_sql = """
        SELECT DISTINCT time as value, str_value as text
        FROM bill_date
        """
        rs = dbhelper.get_result_set(self.env.get_db_cnx(), billing_time_sql)
        for (value, text) in rs.rows:
            billing_info = {'text':text , 'value':value}
            billing_dates.extend([billing_info])
        #self.log.debug("bill-dates: %s"%billing_dates)
        req.hdf['billing_info.billdates'] = billing_dates

    def match_request(self, req):
        if re.search('/Billing', req.path_info):
            return True
        return None

    def process_request(self, req):
        messages = []

        def addMessage(s):
            messages.extend([s]);

        if not re.search('/Billing', req.path_info):
            return None


        if req.method == 'POST':
            if req.args.has_key('setbillingtime'):
                self.set_bill_date(req.authname)
                addMessage("All tickets last bill date updated")
                
        req.hdf["billing_info"] = {"messages": messages,
                                   "href":req.href.Billing(),
                                   "reports": self.get_copy_report_hash_for_render(req),
                                   "usermanual_href":req.href.wiki(user_manual_wiki_title),
                                   "usermanual_title":user_manual_title
                                   }
        self.set_request_billing_dates(req)
        add_stylesheet(req, "Billing/billingplugin.css")
        add_script(req, "Billing/linkifyer.js")
        return 'billing.cs', 'text/html'
        
        
    # ITemplateProvider
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        from pkg_resources import resource_filename
        return [('Billing', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        ClearSilver templates.
        """
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
    

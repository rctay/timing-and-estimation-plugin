from datetime import datetime as dt
import time
from utils import mail
import adw_tracdb as db

#defaultUrl= "https://sekhemt.acceleration.net/ADW/"
_defaultUrl= "https://10.10.10.219/projects"
_htmlLocation = '/var/BigVisibleCharts/Billing'

def cond ( boolExpr, trueResult, falseResult ):
    """ This is the classic ?: operator from languages like C expressed in python (from dive into python)
    """
    return (boolExpr and [trueResult] or [falseResult])[0]



def accumulator():
    var = [0]
    def fn(*params):
        for param in params:
            var[0] = var[0] + param
        return var[0]
    return fn

def progn(*params):
    return params[-1]

def prinTrue(s):
    print s
    return True


def wn (name, attribs, *children):
    return "<%s %s>\n%s\n</%s>\n" % \
           (name, \
            ' '.join(['%s="%s"' % (key, val) for (key, val) in attribs.items()]), \
            '\n'.join([str(c) for c in children]), \
            name)

def ticket_link (number, projUrl):
    return wn('a' , {'href':'/'.join([projUrl,'ticket' ,str(number)])}, "#"+str(number))

def milestone_link (name, projUrl):
    name = str(name)
    return wn('a' , {'href':'/'.join([projUrl,'milestone' ,name])}, name)

def make_project_output(project, rs, totalAcc):
    projAcc = accumulator()
    projLink = '/'.join([_defaultUrl, project ])
    
    def make_cell(idx, val):
        if(idx == rs.columnMap['ticket']):
            val = ticket_link(val, projLink)
        elif idx == rs.columnMap['milestone'] and val != '&nbsp;':
            val = milestone_link(val, projLink)
        elif idx == rs.columnMap['hours']:
            projAcc(float(val))
            totalAcc(float(val))
        return wn('td', {}, val)
    
    return progn(wn('div', {},
                    wn('h2', {},
                       wn('a',{'href':projLink},project)),
                    wn('table', {"cellspacing":"0", "border":"1", "cellpadding":"3"},
                       wn('tr', {},
                          *[wn('th',{}, name) for name in rs.columnNames]),
                       *[wn('tr', {},
                            *[make_cell(idx, val)
                              for idx in range(0, len(row))
                              for val in [row[idx]]])
                         for row in rs.rows]),
                    wn('span',{}, "Total: "+str(projAcc()))))

def make_all_projects_output():
    totalAcc = accumulator()
    sql = """
SELECT
 CASE WHEN t.milestone IS NOT NULL and t.milestone <> '' THEN t.milestone
 ELSE '&nbsp;'
 END as milestone,
 t.id as ticket,
 SUM(newvalue) as hours,
 t.summary as summary,
 strftime('%m/%d/%Y %H:%M:%S', MAX(ticket_change.time), 'unixepoch', 'localtime') as [most-recent-update] ,
 (SELECT CASE WHEN MAX(time) IS NOT NULL THEN strftime('%m/%d/%Y %H:%M:%S', MAX(time), 'unixepoch', 'localtime')
       ELSE 'No previous bill date'
       END as time FROM bill_date ) as [previous-bill-date]
FROM ticket as t
LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
  AND billable.name = 'billable'
JOIN ticket_change on t.id = ticket_change.ticket
  AND (
     ticket_change.time >
     (SELECT CASE WHEN MAX(time) IS NOT NULL THEN MAX(time)
       ELSE 0
       END as time FROM bill_date )
) 
WHERE ticket_change.field = 'hours' 
    AND billable.value=1
GROUP BY t.milestone, t.id
"""

    billingInfo = db.collectResultsFromAllTracs(sql);
    projects_output = '\n'.join([make_project_output(project, rs, totalAcc)
                                 for (project, rs) in billingInfo
                                 if rs.rows ])
    return wn('html', {},
              wn('head', {}),
              wn('body', {},
                 projects_output,
                 wn('span',{},"Total hours billed: "+str(totalAcc()))))


def save_output_to_file(output, when=0):
    if not when:
        when = dt.now()
    fname = '_'.join(["billing", str(when.year),
                      str(when.month), str(when.day),
                      str(when.hour), str(when.minute), ".html"])
    p = "/".join([_htmlLocation, fname])
    print "----"
    print "Writing out billing information to '%s'" % p
    print "----"
    f = open(p, "w")
    f.write(output)
    f.close();



def run_billing(emails="ryan@acceleration.net", when=0):    
    if not when:
        when = dt.now()
    date = '/'.join([str(when.month), str(when.day), str(when.year)])
    
    print "Collecting output..."
    output = make_all_projects_output()
    save_output_to_file(output, when)
    print "Emailing results to %s" % emails
    if emails:
        mail.mail(emails, 'Trac Billing - %s ' % date, output, html=True, fromEmail='trac-tickets@acceleration.net')
    return output
    
    

def add_bill_date(project, username="Timing and Estimation Plugin",  when=0):
    now = time.time()
    if not when:
        when = now
    when = int(when)
    now = int(now)
    sql = """
    INSERT INTO bill_date (time, set_when, str_value)
    VALUES (?, ?, strftime('%m/%d/%Y %H:%M:%S',?, 'unixepoch', 'localtime'))
    """
    db.executeNonQuery(project, sql, when, now, when)

def mark_billing_date_in_all_projects(when=0 ):
    print "Marking the bill date on all projects."
    if not when:
        when = time.time()
    for project in db.projects:
        try:
            add_bill_date(project,  "Timing and Estimation Plugin",  when);
            print "%s Succeeded." % project
        except Exception, e:
            print "* %s failed: %s" % (project , e.args)
    print "Done marking bill dates"
    


             
              
        

from trac.ticket import ITicketChangeListener, Ticket, ITicketManipulator
from trac.core import *
import datetime

def identity(x):
    return x;

def convertfloat(x):
    "some european countries use , as the decimal separator"
    x = str(x).strip()
    if len(x) > 0:
        return float(x.replace(',','.'))
    else: 
        return 0.0


try:
    import trac.util.datefmt
    to_timestamp = trac.util.datefmt.to_timestamp
except Exception:
    to_timestamp = identity


def save_custom_field_value( db, ticket_id, field, value ):
    cursor = db.cursor();
    cursor.execute("SELECT * FROM ticket_custom "
                   "WHERE ticket=%s and name=%s", (ticket_id, field))
    if cursor.fetchone():
        cursor.execute("UPDATE ticket_custom SET value=%s "
                       "WHERE ticket=%s AND name=%s",
                       (value, ticket_id, field))
    else:
        cursor.execute("INSERT INTO ticket_custom (ticket,name, "
                       "value) VALUES(%s,%s,%s)",
                       (ticket_id, field, value))
    db.commit()

DONTUPDATE = "DONTUPDATE"

def save_ticket_change( db, ticket_id, author, change_time, field, oldvalue, newvalue, log, dontinsert=False):
    """tries to save a ticket change,

       dontinsert means do not add the change if it didnt already exist
    """
    if type(change_time) == datetime.datetime:
        change_time = to_timestamp(change_time)
    cursor = db.cursor();
    sql = """SELECT * FROM ticket_change
             WHERE ticket=%s and author=%s and time=%s and field=%s"""

    cursor.execute(sql, (ticket_id, author, change_time, field))
    if cursor.fetchone():
        if oldvalue == DONTUPDATE:
            cursor.execute("""UPDATE ticket_change  SET  newvalue=%s
                       WHERE ticket=%s and author=%s and time=%s and field=%s""",
                           ( newvalue, ticket_id, author, change_time, field))

        else:
            cursor.execute("""UPDATE ticket_change  SET oldvalue=%s, newvalue=%s
                       WHERE ticket=%s and author=%s and time=%s and field=%s""",
                           (oldvalue, newvalue, ticket_id, author, change_time, field))
    else:
        if oldvalue == DONTUPDATE:
            oldvalue = '0'
        if not dontinsert:
            cursor.execute("""INSERT INTO ticket_change  (ticket,time,author,field, oldvalue, newvalue)
                        VALUES(%s, %s, %s, %s, %s, %s)""",
                           (ticket_id, change_time, author, field, oldvalue, newvalue))
    db.commit()

class TimeTrackingTicketObserver(Component):
    implements(ITicketChangeListener)
    def __init__(self):
        pass

    def watch_hours(self, ticket):

        def readTicketValue(name, tipe, default=0):
            if ticket.values.has_key(name):
                return tipe(ticket.values[name] or default)
            else:
                cursor = self.env.get_db_cnx().cursor()
                cursor.execute("SELECT * FROM ticket_custom where ticket=%s and name=%s" , (ticket.id, name))
                val = cursor.fetchone()
                if val:
                    return tipe(val[2] or default)
                return default


        hours = readTicketValue("hours", convertfloat)
        totalHours = readTicketValue("totalhours", convertfloat)

        db = self.env.get_db_cnx()
        ticket_id = ticket.id
        cl = ticket.get_changelog()

        self.log.debug("found hours: "+str(hours ));
        #self.log.debug("Dir_ticket:"+str(dir(ticket)))
        #self.log.debug("ticket.values:"+str(ticket.values))
        #self.log.debug("changelog:"+str(cl))

        most_recent_change = None
        if cl:
            most_recent_change = cl[-1];
            change_time = most_recent_change[0]
            author = most_recent_change[1]
        else:
            change_time = ticket.time_created
            author = ticket.values["reporter"]


        ## SAVE estimated hour
        estimatedhours = readTicketValue("estimatedhours", convertfloat)
        self.log.debug("found Estimated hours:"+str(estimatedhours))
        db = self.env.get_db_cnx()
        save_ticket_change( db, ticket_id, author, change_time, "estimatedhours", DONTUPDATE, str(estimatedhours), self.log, True)
        save_custom_field_value( db, ticket.id, "estimatedhours", str(estimatedhours))
        db.commit();
        #######################


        ## If our hours changed
        if not hours == 0:
            newtotal = str(totalHours+hours)
            save_ticket_change( db, ticket_id, author, change_time, "hours", '0.0', str(hours), self.log)
            save_ticket_change( db, ticket_id, author, change_time, "totalhours", str(totalHours), str(newtotal), self.log)
            save_custom_field_value( db, ticket_id, "hours", '0')
            save_custom_field_value( db, ticket_id, "totalhours", str(newtotal) )
        ########################

    # END of watch_hours

    def ticket_created(self, ticket):
        """Called when a ticket is created."""
        self.watch_hours(ticket)


    def ticket_changed(self, ticket, comment, author, old_values):
        """Called when a ticket is modified.

        `old_values` is a dictionary containing the previous values of the
        fields that have changed.
        """
        self.watch_hours(ticket)

    def ticket_deleted(self, ticket):
        """Called when a ticket is deleted."""


class TimeTrackingTicketValidator(Component):
    implements(ITicketManipulator)

    def __init__(self):
        pass

    def prepare_ticket(req, ticket, fields, actions):
        """not currently called"""

    def validate_ticket(self, req, ticket):
        """Validate a ticket after it's been populated from user input.

        Must return a list of `(field, message)` tuples, one for each problem
        detected. `field` can be `None` to indicate an overall problem with the
        ticket. Therefore, a return value of `[]` means everything is OK."""
        errors = []
        #some european countries use , as the decimal separator
        try:
            convertfloat(ticket.values['hours'])
        except KeyError:
            self.log.exception("The hours field was not submitted")
        except ValueError:
            errors.append(('Add Hours to Ticket', 'Value must be a number'))
        try:
            convertfloat(ticket.values['estimatedhours'])
        except KeyError:
            self.log.exception("The estimatedhours field was not submitted")
        except ValueError:
            errors.append(('Estimated Number of Hours', 'Value must be a number'))
        return errors

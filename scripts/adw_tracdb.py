from pysqlite2 import dbapi2 as sqlite
from datetime import datetime, timedelta
from time import mktime
import os

tracDir = '/var/trac'
projectDBLocationFormat = '/var/trac/%s/db/trac.db'
# all directories in the trac directory
projects = [f for f in os.listdir(tracDir) if os.path.isdir('/'.join ([tracDir, f]))]

def makeDb(proj):
    return projectDBLocationFormat % proj

def collectResultsFromAllTracs( sql ):
    lst = []
    for proj in projects:
        try:
            lst.extend([( proj , getResultSet( proj, sql ))])
        except Exception, e:
            print "collectResultsFromAllTracs: sql failed to execute on %s : %s " % (proj, e.args)
            
    return lst

def executeAgainstAllTracs( sql ):
    for proj in projects:
        try:
            executeNonQuery( proj, sql )
        except:
            print "executeAgainstAllTracs: sql failed to execute on %s" % proj
    

def executeNonQuery(proj, sql, *params):
    """Executes the query on the given project"""
    con = sqlite.connect(makeDb(proj))
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        con.commit()
    finally:
        cur.close()
        con.close()

def getColumnAsList(db, sql, col=0, *params):
    return [valueList[col] for valueList in get_all(db, sql, *params)[1]]

def getScalar(proj , sql, col=0, *params):
    db = sqlite.connect(makeDb(proj))
    cur = db.cursor()
    try:
        cur.execute(sql, params)
        data = cur.fetchone()
    finally:
        cur.close()
    return data[col]


def getVector(proj, sql, *params):
    db = sqlite.connect(makeDb(proj))
    cur = db.cursor()
    try:
        cur.execute(sql, params)
        data = cur.fetchone()
    finally:
        cur.close()
    return data

def getAll(proj, sql, *params):
    """Executes the query and returns the (description, data)"""
    con = sqlite.connect(makeDb(proj)) 
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        data = cur.fetchall()
        desc = cur.description
    finally:
        cur.close()
        con.close()
    return (desc, data)
       
def getResultSet(proj, sql, *params):
    """Executes the query and returns a Result Set"""
    return ResultSet(getAll(proj, sql, *params))

def _columnName( columnDescription ):
    """ given a the columnHeader from the result set from getAll gives you the column Headers """
    return columnDescription[0];

class ResultSet:
    """ the result of calling getResultSet """
    def __init__ (self, (columnDescription, rows)):
        self.columnDescription, self.rows = columnDescription, rows
        self.columnNames = [_columnName(_) for _ in self.columnDescription]
        self.columnMap = self.getColumnMap()

    def getColumnMap ( self ):
        """This function will take the result set from getAll and will
        return a hash of the column names to their index """
        h = {}
        i = 0
        if self.columnDescription:
            for col in self.columnNames:
                h[ col ] = i
                i+=1
        return h;
    
    def value(self, col, row ):
        """ given a row(list or idx) and a column( name or idx ), retrieve the appropriate value"""
        tcol = type(col)
        trow = type(row)
        if tcol == str:
            if(trow == list or trow == tuple):
                return row[self.columnMap[col]]
            elif(trow == int):
                return self.rows[row][self.columnMap[col]]
            else:
                print ("rs.value Type Failed col:%s  row:%s" % (type(col), type(row)))
        elif tcol == int:
            if(trow == list or trow == tuple):
                return row[col]
            elif(trow == int):
                return self.rows[row][col]
            else:
                print ("rs.value Type Failed col:%s  row:%s" % (type(col), type(row)))
        else:
            print ("rs.value Type Failed col:%s  row:%s" % (type(col), type(row)))
            



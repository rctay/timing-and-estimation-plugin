
def get_all(com, sql, *params):
    """Executes the query and returns the (description, data)"""
    db = com.env.get_db_cnx()
    cur = db.cursor()
    desc  = None
    data = None
    try:
        cur.execute(sql, params)
        data = list(cur.fetchall())
        desc = cur.description
        db.commit();
    except Exception, e:
        com.log.error('There was a problem executing sql:%s \n \
with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback();
    try:
        db.close()
    except:
        pass

    return (desc, data)

def execute_non_query(com,  sql, *params):
    """Executes the query on the given project"""
    db = com.env.get_db_cnx()
    cur = db.cursor()
    try:
        cur.execute(sql, params)
        db.commit()
    except Exception, e:
        com.log.error('There was a problem executing sql:%s \n \
with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback();
    try:
        db.close()
    except:
        pass

def get_first_row(com,  sql,*params):
    """ Returns the first row of the query results as a tuple of values (or None)"""
    db = com.env.get_db_cnx()
    cur = db.cursor()
    data = None;
    try:
        cur.execute(sql, params)
        data = cur.fetchone();
        db.commit();
    except Exception, e:
        com.log.error('There was a problem executing sql:%s \n \
        with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback()
    try:
        db.close()
    except:
        pass
    return data;

def get_scalar(com, sql, col=0, *params):
    """ Gets a single value (in the specified column) from the result set of the query"""
    data = get_first_row(com, sql, *params);
    if data:
        return data[col]
    else:
        return None;

def execute_in_trans(com, *args):
    db = com.env.get_db_cnx()
    cur = db.cursor()
    result = True
    try:
        for sql, params in args:
            cur.execute(sql, params)
        db.commit()
    except Exception, e:
        com.log.error('There was a problem executing sql:%s \n \
        with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback();
        result = e
    try:
        db.close()
    except:
        pass
    return result

def db_table_exists(com,  table):
    db = com.env.get_db_cnx()
    sql = "SELECT * FROM %s LIMIT 1" % table;
    cur = db.cursor()
    has_table = True;
    try:
        cur.execute(sql)
        db.commit()
    except Exception, e:
        has_table = False
        db.rollback()

    try:
        db.close()
    except:
        pass
    return has_table

def get_column_as_list(com, sql, col=0, *params):
    data = get_all(com, sql, *params)[1] or ()
    return [valueList[col] for valueList in data]

def get_system_value(com, key):
    return get_scalar(com, "SELECT value FROM system WHERE name=%s", 0, key)

def set_system_value(com, key, value):
    if get_system_value(com, key):
        execute_non_query(com, "UPDATE system SET value=%s WHERE name=%s", value, key)
    else:
        execute_non_query(com, "INSERT INTO system (value, name) VALUES (%s, %s)",
            value, key)


def get_result_set(com, sql, *params):
    """Executes the query and returns a Result Set"""
    tpl = get_all(com, sql, *params);
    if tpl and tpl[0] and tpl[1]:
        return ResultSet(tpl)
    else:
        return None


class ResultSet:
    """ the result of calling getResultSet """
    def __init__ (self, (columnDescription, rows)):
        self.columnDescription, self.rows = columnDescription, rows
        self.columnMap = self.get_column_map()

    def get_column_map ( self ):
        """This function will take the result set from getAll and will
        return a hash of the column names to their index """
        h = {}
        i = 0
        if self.columnDescription:
            for col in self.columnDescription:
                h[ col[0] ] = i
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

    def json_out(self):
        json = "[%s]" % ',\r\n'. join(
            [("{%s}" % ','.join(
            ["'%s':'%s'" %
             (key, str(self.value(val, row)).
              replace("'","\\'").
              replace('"','\\"').
              replace('\r','\\r').
              replace('\n','\\n'))
             for (key, val) in self.columnMap.items()]))
             for row in self.rows])
        #mylog.debug('serializing to json : %s'% json)
        return json

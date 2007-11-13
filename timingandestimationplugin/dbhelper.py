mylog = None;


def get_all(db, sql, *params):
    """Executes the query and returns the (description, data)"""
    cur = db.cursor()
    desc  = None
    data = None
    try:
        cur.execute(sql, params)
        data = list(cur.fetchall())
        desc = cur.description
        db.commit();
    except Exception, e:
        mylog.error('There was a problem executing sql:%s \n \
with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback();
    try:
        db.close()
    except:
        pass
    
    return (desc, data)

def get_first_row(db,sql,*params):
    rows = get_all (db, sql, *params)[1]
    if rows:
        return rows[0]
    return None

def execute_non_query(db, sql, *params):
    """Executes the query on the given project"""
    cur = db.cursor()
    try:
        cur.execute(sql, params)
        db.commit()
    except Exception, e:
        mylog.error('There was a problem executing sql:%s \n \
with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback();
    try:
        db.close()
    except:
        pass

def get_scalar(db, sql, col=0, *params):
    cur = db.cursor()
    data = None;
    try:
        cur.execute(sql, params)
        data = cur.fetchone();
        db.commit();
    except Exception, e:
        mylog.error('There was a problem executing sql:%s \n \
with parameters:%s\nException:%s'%(sql, params, e));
        db.rollback()
    try:
        db.close()
    except:
        pass
    if data:
        return data[col]
    else:
        return None;

def db_table_exists(db, table):
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

def get_column_as_list(db, sql, col=0, *params):
    return [valueList[col] for valueList in get_all(db, sql, *params)[1]]

def get_system_value(db, key):
    return get_scalar(db, "SELECT value FROM system WHERE name=%s", 0, key)

def set_system_value(env,  key, value):
    if get_system_value(env.get_db_cnx(), key):
        execute_non_query(env.get_db_cnx(), "UPDATE system SET value=%s WHERE name=%s", value, key)        
    else:
        execute_non_query(env.get_db_cnx(), "INSERT INTO system (value, name) VALUES (%s, %s)",
            value, key)


def get_result_set(db, sql, *params):
    """Executes the query and returns a Result Set"""
    return ResultSet(get_all(db, sql, *params))


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
   

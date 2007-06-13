db_version_key = 'TimingAndEstimationPlugin_Db_Version';
db_version = 3
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

def get_plugin_db_version(db):
    sql = "SELECT value FROM system where name = '%s';" % db_version_key
    val = get_scalar(db, sql)
    return val;

def set_plugin_db_version(db_fn):
    if get_plugin_db_version(db_fn()):
        sql = "UPDATE system SET value='%s' WHERE name = '%s'" % (db_version, db_version_key)
    else:
        sql = "INSERT INTO system (name, value) VALUES( '%s', '%s') " % ( db_version_key, str(db_version) )
    execute_non_query(db_fn(), sql);

def db_needs_upgrade(db):
    ver = get_plugin_db_version(db);
    if not ver or int(ver) < int(db_version):
        return True
    return False

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
   

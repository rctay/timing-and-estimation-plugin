

def up ( db_fn, helper ):
    print "Running migrate version 4"
    sql ="""
    ALTER TABLE report_version ADD COLUMN tags varchar(1024) null;
    """
    helper.execute_non_query(db_fn(), sql)



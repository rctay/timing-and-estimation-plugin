import dbhelper
from trac.ticket.default_workflow import get_workflow_config
try: 
    set 
except NameError: 
    from sets import Set as set     # Python 2.3 fallback 

def status_variables(statuses):
    return ', '.join(['$'+i.upper().replace("_","").replace(" ","") for i in list(statuses)])

def get_statuses(com):
    config = com.config
    stats = get_statuses_from_workflow(config)
    status_sql = """
    SELECT DISTINCT status FROM ticket WHERE status <> '' ;
    """
    stats |= set(dbhelper.get_column_as_list(com, status_sql))
    stats.difference_update(['', None])
    return stats

def get_statuses_from_workflow(config):
    wf = get_workflow_config(config)
    x = set()
    for key, value in wf.items():
        x.add(value['newstate'])
        x |= set(value['oldstates'])
    x.difference_update([u'*'])
    return x

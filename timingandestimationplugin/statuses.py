import dbhelper
from trac.ticket.default_workflow import get_workflow_config
from sets import Set

def status_variables(statuses):
    return ', '.join(['$'+i.upper() for i in list(statuses)])
                     
def get_statuses(config, env):
    stats = get_statuses_from_workflow(config)
    status_sql = """
    SELECT DISTINCT status FROM ticket WHERE status <> '' ;
    """
    stats |= Set(dbhelper.get_column_as_list(env.get_db_cnx(), status_sql))
    stats.difference_update(['', None])
    return stats

def get_statuses_from_workflow(config):
    wf = get_workflow_config(config)
    x = Set()
    for key, value in wf.items():
        x.add(value['newstate'])
        x |= Set(value['oldstates'])
    x.difference_update([u'*'])
    return x

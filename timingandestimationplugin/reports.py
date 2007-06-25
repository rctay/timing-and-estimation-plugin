# IF YOU ADD A NEW SECTION OF REPORTS, You will need to make
# sure that section is also added to the all_reports hashtable
# near the bottom

#Please try to keep this clean"

billing_reports = [
        {
    "title":"Ticket Work Summary",
    "reportnumber":None,
    "version":13,
    "sql":"""
SELECT __ticket__ as __group__, __style__, __ticket__,
newvalue as Work_added, author, time, _ord
FROM(
  SELECT '' as __style__, author, t.id as __ticket__,
  CAST(newvalue as DECIMAL) as newvalue, ticket_change.time as time, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  
  UNION 
  
  SELECT 'background-color:#DFE;' as __style__,
    'Total work done on the ticket in the selected time period ' as author,
    t.id as __ticket__, sum( CAST(newvalue as DECIMAL) ) as newvalue,
    NULL as time, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By t.id
)  as tbl
ORDER BY __ticket__, _ord ASC, time ASC

    """
    },#END Ticket work summary
        {
    "title":"Milestone Work Summary",
    "reportnumber":None,
    "version":12,
    "sql":"""

SELECT 
  milestone as __group__, __style__,  ticket, summary, newvalue as Work_added,
  time, _ord
FROM(
  SELECT '' as __style__, t.id as ticket,
    SUM(CAST(newvalue as DECIMAL)) as newvalue, t.summary as summary,
    MAX(ticket_change.time) as time, t.milestone as milestone, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP BY t.milestone, t.id, t.summary
  
  UNION 
  
  SELECT 'background-color:#DFE;' as __style__, NULL as ticket,
    sum(CAST(newvalue as DECIMAL)) as newvalue, 'Total work done' as summary,
    NULL as time, t.milestone as milestone, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By t.milestone
)  as tbl
ORDER BY milestone,  _ord ASC, ticket, time



    """
    },#END Milestone work summary
        
    {
    "title":"Developer Work Summary",
    "reportnumber":None,
    "version":12,
    "sql":"""
SELECT author as __group__,__style__, ticket,
  newvalue as Work_added, time as time, _ord
FROM(
  SELECT '' as __style__, author, cast(t.id as text) as ticket,
    CAST(newvalue as DECIMAL) as newvalue, ticket_change.time as time, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
      
  UNION 
  
  SELECT 'background-color:#DFE;' as __style__, author, NULL as ticket,
    sum(CAST(newvalue as DECIMAL)) as newvalue, NULL as time, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id 
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By author
)  as tbl
ORDER BY author,  _ord ASC, time
    
    """
    },#END Hours Per Developer
]
ticket_hours_reports = [
{
    "title": "Ticket Hours",
    "reportnumber": None,
    "version":9,
    "sql": """
SELECT __color__, __style__, ticket, summary, component ,version, severity,
  milestone, status, owner, Estimated_work, Total_work, billable,_ord
FROM (
  SELECT p.value AS __color__,
    '' as __style__,
    t.id AS ticket, summary AS summary,             -- ## Break line here
    component,version, severity, milestone, status, owner,
    CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
    CAST(totalhours.value as DECIMAL) as Total_work, 
    CASE WHEN billable.value = 1 THEN 'Y' else 'N' END as billable,
    time AS created, changetime AS modified,         -- ## Dates are formatted
    description AS _description_,                    -- ## Uses a full row
    changetime AS _changetime,
    reporter AS _reporter
    ,0 as _ord                                        
  	
    FROM ticket as t
    JOIN enum as p ON p.name=t.priority AND p.type='priority'
    
  LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
        AND EstimatedHours.Ticket = t.Id
  LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
        AND totalhours.Ticket = t.Id
  LEFT JOIN ticket_custom as billable ON billable.name='billable'
        AND billable.Ticket = t.Id
  
    WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
    
  
  UNION 
  
  SELECT '1' AS __color__,
         'background-color:#DFE;' as __style__,
         NULL as ticket, 'Total' AS summary,             
         NULL as component,NULL as version, NULL as severity, NULL as  milestone, NULL as status, NULL as owner,
         SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
         SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
         NULL as billable,
         NULL as created, NULL as modified,         -- ## Dates are formatted
  
         NULL AS _description_,
         NULL AS _changetime,
         NULL AS _reporter
         ,1 as _ord
    FROM ticket as t
    JOIN enum as p ON p.name=t.priority AND p.type='priority'
    
  LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
        AND EstimatedHours.Ticket = t.Id
  
  LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
        AND totalhours.Ticket = t.Id
  
  LEFT JOIN ticket_custom as billable ON billable.name='billable'
        AND billable.Ticket = t.Id
    
    WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
      AND billable.value in ($BILLABLE, $UNBILLABLE)
)  as tbl
ORDER BY  _ord ASC, ticket
    """
    },
#END Ticket Hours 
{
    "title": "Ticket Hours with Description",
    "reportnumber": None,
    "version":10,
    "sql": """
SELECT __color__,  __style__,  ticket, summary, component ,version, severity,
 milestone, status, owner, Estimated_work, Total_work, billable
--,created,  modified,         -- ## Dates are formatted
,_description_
-- _changetime,
-- _reporter
,_ord

FROM (
SELECT p.value AS __color__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component,version, severity, milestone, status, owner,
       CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
       CAST(totalhours.value as DECIMAL) as Total_work,
       CASE WHEN billable.value = 1 THEN 'Y'
            else 'N'
       END as billable,
       time AS created, changetime AS modified,         -- ## Dates are formatted
       description AS _description_,                    -- ## Uses a full row
       changetime AS _changetime,
       reporter AS _reporter
       ,0 as _ord                                        
	
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id
LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id
LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id

  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  

UNION 

SELECT '1' AS __color__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total' AS summary,             
       NULL as component,NULL as version, NULL as severity, NULL as  milestone, NULL as status, NULL as owner,
       SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
       SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
       NULL as billable,
       NULL as created, NULL as modified,         -- ## Dates are formatted

       NULL AS _description_,
       NULL AS _changetime,
       NULL AS _reporter
       ,1 as _ord
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id

LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id

LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id
  
  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
)  as tbl
ORDER BY _ord ASC, ticket
    """
    },
#END Ticket Hours 

    {
    "title":"Ticket Hours Grouped By Component",
    "reportnumber":None,
    "version":9,
    "sql": """
SELECT __color__, __group__, __style__, ticket, summary, __component__ ,version,
  severity, milestone, status, owner, Estimated_work, total_work, billable,
  _ord

FROM (
SELECT p.value AS __color__,
       t.component AS __group__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component as __component__,version, severity, milestone, status, owner,
       CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
       CAST(totalhours.value as DECIMAL) as Total_work,
       CASE WHEN billable.value = 1 THEN 'Y'
            else 'N'
       END as billable,
       time AS created, changetime AS modified,         -- ## Dates are formatted
       description AS _description_,                    -- ## Uses a full row
       changetime AS _changetime,
       reporter AS _reporter
       ,0 as _ord                                        
	
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id
LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id
LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id

  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  

UNION 

SELECT '1' AS __color__,
       t.component AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,             
       t.component as __component__, NULL as version, NULL as severity,
       NULL as  milestone, NULL as status,
       NULL as owner,
       SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
       SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
       NULL as billable,
       NULL as created,
       NULL as modified,         -- ## Dates are formatted

       NULL AS _description_,
       NULL AS _changetime,
       NULL AS _reporter
       ,1 as _ord
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id

LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id

LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id
  
  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.component
)  as tbl
ORDER BY __component__, _ord ASC,ticket
    """
    },
# END Ticket Hours  GROUPED BY COMPONENT
    
    {
    "title":"Ticket Hours Grouped By Component with Description",
    "reportnumber":None,
    "version":8,
    "sql": """
SELECT __color__, __group__, __style__,  ticket, summary, __component__ ,
  version, severity, milestone, status, owner, Estimated_work, Total_work,
  billable, _description_, _ord

FROM (
SELECT p.value AS __color__,
       t.component AS __group__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component as __component__, version, severity, milestone, status, owner,
       CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
       CAST(totalhours.value as DECIMAL) as Total_work,
       CASE WHEN billable.value = 1 THEN 'Y' else 'N' END as billable,
       time AS created, changetime AS modified,         -- ## Dates are formatted
       description AS _description_,                    -- ## Uses a full row
       changetime AS _changetime,
       reporter AS _reporter
       ,0 as _ord                                        
	
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id
LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id
LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id

  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  

UNION 

SELECT '1' AS __color__,
       t.component AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,             
       t.component as __component__, NULL as version, NULL as severity,
       NULL as  milestone, NULL as status, NULL as owner,
       SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
       SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
       NULL as billable,
       NULL as created, NULL as modified,         -- ## Dates are formatted

       NULL AS _description_,
       NULL AS _changetime,
       NULL AS _reporter
       ,1 as _ord
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id

LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id

LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id
  
  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.component
)  as tbl
ORDER BY __component__, _ord ASC, ticket
    """
    },
# END Ticket Hours Grouped BY Component with Description
    {
    "title":"Ticket Hours Grouped By Milestone",
    "reportnumber":None,
    "version":9,
    "sql": """
SELECT __color__, __group__, __style__,  ticket, summary, component ,version,
  severity, __milestone__, status, owner, Estimated_work, Total_work, billable,
  _ord

FROM (
SELECT p.value AS __color__,
       t.milestone AS __group__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component,version, severity, milestone as __milestone__, status, owner,
       CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
       CAST(totalhours.value as DECIMAL) as Total_work,
       CASE WHEN billable.value = 1 THEN 'Y'
            else 'N'
       END as billable,
       time AS created, changetime AS modified,         -- ## Dates are formatted
       description AS _description_,                    -- ## Uses a full row
       changetime AS _changetime,
       reporter AS _reporter, 0 as _ord                                        
	
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id
LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id
LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id

  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  

UNION 

SELECT '1' AS __color__,
       t.milestone AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,             
       NULL as component,NULL as version, NULL as severity,
       t.milestone as  __milestone__, NULL as status, NULL as owner,
       SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
       SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
       NULL as billable,
       NULL as created, NULL as modified,         -- ## Dates are formatted

       NULL AS _description_,
       NULL AS _changetime,
       NULL AS _reporter
       ,1 as _ord
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id

LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id

LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id
  
  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.milestone
)  as tbl
ORDER BY __milestone__, _ord ASC, ticket
    """
    },
#END Ticket Hours Grouped By MileStone
        {
    "title":"Ticket Hours Grouped By MileStone with Description",
    "reportnumber":None,
    "version":9,
    "sql": """
SELECT __color__, __group__, __style__,  ticket, summary, component ,version, severity,
 __milestone__, status, owner, Estimated_work, Total_work, billable,
 _description_, _ord

FROM (
SELECT p.value AS __color__,
       t.milestone AS __group__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component,version, severity, milestone as __milestone__, status, owner,
       CAST(EstimatedHours.value as DECIMAL) as Estimated_work,
       CAST(totalhours.value as DECIMAL) as Total_work,
       CASE WHEN billable.value = 1 THEN 'Y'
            else 'N'
       END as billable,
       time AS created, changetime AS modified,         -- ## Dates are formatted
       description AS _description_,                    -- ## Uses a full row
       changetime AS _changetime,
       reporter AS _reporter
       ,0 as _ord                                        
	
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id
LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id
LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id

  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  

UNION 

SELECT '1' AS __color__,
       t.milestone AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,             
       NULL as component,NULL as version, NULL as severity,
       t.milestone as __milestone__,
       NULL as status, NULL as owner,
       SUM(CAST(EstimatedHours.value as DECIMAL)) as Estimated_work,
       SUM(CAST(totalhours.value as DECIMAL)) as Total_work,
       NULL as billable,
       NULL as created, NULL as modified,         -- ## Dates are formatted
       NULL AS _description_,
       NULL AS _changetime,
       NULL AS _reporter, 1 as _ord
  FROM ticket as t
  JOIN enum as p ON p.name=t.priority AND p.type='priority'
  
LEFT JOIN ticket_custom as EstimatedHours ON EstimatedHours.name='estimatedhours'
      AND EstimatedHours.Ticket = t.Id

LEFT JOIN ticket_custom as totalhours ON totalhours.name='totalhours'
      AND totalhours.Ticket = t.Id

LEFT JOIN ticket_custom as billable ON billable.name='billable'
      AND billable.Ticket = t.Id
  
  WHERE t.status IN ($NEW, $ASSIGNED, $REOPENED, $CLOSED) 
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.milestone
)  as tbl
ORDER BY __milestone__, _ord ASC, ticket
    """
    }
    #END Ticket Hours Grouped By MileStone with Description
]
    
all_reports = [
    {"title":"Billing Reports",
     "reports":billing_reports},
    {"title":"Ticket/Hour Reports",
     "reports": ticket_hours_reports}
    ]

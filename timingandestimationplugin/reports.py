# IF YOU ADD A NEW SECTION OF REPORTS, You will need to make
# sure that section is also added to the all_reports hashtable
# near the bottom

#Please try to keep this clean"

billing_reports = [
        {
    "uuid":"b24f08c0-d41f-4c63-93a5-25e18a8513c2",
    "title":"Ticket Work Summary",
    "version":20,
    "sql":"""
SELECT __ticket__ as __group__, __style__, ticket,
newvalue as Work_added, author, time as datetime, _ord
FROM(
  SELECT '' as __style__, author,
  t.summary as __ticket__,
  t.id as ticket,
  CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
    ELSE CAST( newvalue AS DECIMAL ) END AS newvalue,
  ticket_change.time as time, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE

  UNION

  SELECT 'background-color:#DFE;' as __style__,
    'Total work done on the ticket in the selected time period ' as author,
    t.summary as __ticket__,
    t.id as ticket,
  SUM( CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
         ELSE CAST( newvalue AS DECIMAL ) END ) as newvalue,
    NULL as time, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By t.id, t.summary
)  as tbl
ORDER BY __ticket__, _ord ASC, time ASC

    """
    },#END Ticket work summary
        {
    "uuid":"af13564f-0e36-4a17-96c0-632dc68d8d14",
    "title":"Milestone Work Summary",
    "version":17,
    "sql":"""

SELECT
  milestone as __group__, __style__,  ticket, summary, newvalue as Work_added,
  time  as datetime, _ord
FROM(
  SELECT '' as __style__, t.id as ticket,
    SUM( CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
         ELSE CAST( newvalue AS DECIMAL ) END) as newvalue, t.summary as summary,
    MAX(ticket_change.time) as time, t.milestone as milestone, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP BY t.milestone, t.id, t.summary

  UNION

  SELECT 'background-color:#DFE;' as __style__, NULL as ticket,
    sum( CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
         ELSE CAST( newvalue AS DECIMAL ) END) as newvalue, 'Total work done' as summary,
    NULL as time, t.milestone as milestone, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By t.milestone
)  as tbl
ORDER BY milestone,  _ord ASC, ticket, time



    """
    },#END Milestone work summary

    {
    "uuid":"7bd4b0ce-da6d-4b11-8be3-07e65b540d99",
    "title":"Developer Work Summary",
    "version":17,
    "sql":"""
SELECT author as __group__,__style__, ticket, summary,
  newvalue as Work_added, time as datetime, _ord
FROM(
  SELECT '' as __style__, author, t.id  as ticket,
    t.summary as summary,
    CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
         ELSE CAST( newvalue AS DECIMAL ) END as newvalue,
    ticket_change.time as time, 0 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE

  UNION

  SELECT 'background-color:#DFE;' as __style__, author, NULL as ticket,
    Null as summary,
    SUM( CASE WHEN newvalue = '' OR newvalue IS NULL THEN 0
         ELSE CAST( newvalue AS DECIMAL ) END) as newvalue,
    NULL as time, 1 as _ord
  FROM ticket_change
  JOIN ticket t on t.id = ticket_change.ticket
  LEFT JOIN ticket_custom as billable on billable.ticket = t.id
    and billable.name = 'billable'
  WHERE field = 'hours' and
    t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
      AND ticket_change.time >= $STARTDATE
      AND ticket_change.time < $ENDDATE
  GROUP By author
)  as tbl
ORDER BY author,  _ord ASC, time

    """
    },#END Hours Per Developer
]
th_version =15
ticket_hours_reports = [
{
    "uuid":"8d785cdb-dcf5-43c9-b2a6-216997b0011a",
    "title": "Ticket Hours",
    "version":th_version,
    "sql": """
SELECT __color__, __style__, ticket, summary, component ,version, severity,
  milestone, status, owner, Estimated_work, Total_work, billable,_ord
FROM (
  SELECT p.value AS __color__,
    '' as __style__,
    t.id AS ticket, summary AS summary,             -- ## Break line here
    component,version, severity, milestone, status, owner,
    CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
      ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
    CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
      ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
    CASE WHEN billable.value = '1' THEN 'Y' else 'N' END as billable,
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

    WHERE t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)


  UNION

  SELECT '1' AS __color__,
         'background-color:#DFE;' as __style__,
         NULL as ticket, 'Total' AS summary,
         NULL as component,NULL as version, NULL as severity, NULL as  milestone,
         'Time Remaining: ' as status,
         CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512))  as owner,
         SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
      ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
         SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
      ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

    WHERE t.status IN (#STATUSES#)
      AND billable.value in ($BILLABLE, $UNBILLABLE)
)  as tbl
ORDER BY  _ord ASC, ticket
    """
    },
#END Ticket Hours
{
    "uuid":"71e7c36d-e512-4d0b-b499-087d4d20ff0b",
    "title": "Ticket Hours with Description",
    "version":th_version,
    "sql": """
SELECT __color__,  __style__,  ticket, summary, component ,version, severity,
 milestone, status, owner, Estimated_work, Total_work, billable
-- ## ,created,  modified,         -- ## Dates are formatted
,_description_
-- ## _changetime,
-- ## _reporter
,_ord

FROM (
SELECT p.value AS __color__,
       '' as __style__,
       t.id AS ticket, summary AS summary,             -- ## Break line here
       component,version, severity, milestone, status, owner,
       CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
      ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
       CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
      ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
       CASE WHEN billable.value = '1' THEN 'Y'
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)


UNION

SELECT '1' AS __color__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total' AS summary,
       NULL as component,NULL as version, NULL as severity, NULL as  milestone,
       'Time Remaining: ' as status,
       CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512))  as owner,
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)
)  as tbl
ORDER BY _ord ASC, ticket
    """
    },
#END Ticket Hours

    {
    "uuid":"5f33b102-e6a6-47e8-976c-ac7a6794a909",
    "title":"Ticket Hours Grouped By Component",
    "version":th_version,
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
       CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
       CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
       CASE WHEN billable.value = '1' THEN 'Y'
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)


UNION

SELECT '1' AS __color__,
       t.component AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,
       t.component as __component__, NULL as version, NULL as severity,
       NULL as  milestone, 'Time Remaining: ' as status,
       CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512))  as owner,
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.component
)  as tbl
ORDER BY __component__, _ord ASC,ticket
    """
    },
# END Ticket Hours  GROUPED BY COMPONENT

    {
    "uuid":"7816f034-a174-4a94-aed6-358fb648b2fc",
    "title":"Ticket Hours Grouped By Component with Description",
    "version":th_version,
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
       CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
       CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
       CASE WHEN billable.value = '1' THEN 'Y' else 'N' END as billable,
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)


UNION

SELECT '1' AS __color__,
       t.component AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,
       t.component as __component__, NULL as version, NULL as severity,
       NULL as  milestone, 'Time Remaining: ' as status,
       CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512))  as owner,
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.component
)  as tbl
ORDER BY __component__, _ord ASC, ticket
    """
    },
# END Ticket Hours Grouped BY Component with Description
    {
    "uuid":"03815803-7688-4f3a-8e65-8d254cc1d1fb",
    "title":"Ticket Hours Grouped By Milestone",
    "version":th_version,
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
       CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
       CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
       CASE WHEN billable.value = '1' THEN 'Y'
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)


UNION

SELECT '1' AS __color__,
       t.milestone AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,
       NULL as component,NULL as version, NULL as severity,
       t.milestone as  __milestone__, 'Time Remaining: ' as status,
       CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512)) as owner,
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)
  GROUP BY t.milestone
)  as tbl
ORDER BY __milestone__, _ord ASC, ticket
    """
    },
#END Ticket Hours Grouped By MileStone
        {
    "uuid":"040c9025-7641-4d18-96ad-2b26b4095566",
    "title":"Ticket Hours Grouped By MileStone with Description",
    "version":th_version,
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
       CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END as Estimated_work,
       CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END as Total_work,
       CASE WHEN billable.value = '1' THEN 'Y'
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

  WHERE t.status IN (#STATUSES#)
    AND billable.value in ($BILLABLE, $UNBILLABLE)


UNION

SELECT '1' AS __color__,
       t.milestone AS __group__,
       'background-color:#DFE;' as __style__,
       NULL as ticket, 'Total work' AS summary,
       NULL as component,NULL as version, NULL as severity,
       t.milestone as __milestone__,
       'Time Remaining: ' as status,
       CAST(
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) -
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END)
         AS CHAR(512)) as owner,
       SUM(CASE WHEN EstimatedHours.value = '' OR EstimatedHours.value IS NULL THEN 0
         ELSE CAST( EstimatedHours.value AS DECIMAL ) END) as Estimated_work,
       SUM(CASE WHEN totalhours.value = '' OR totalhours.value IS NULL THEN 0
         ELSE CAST( totalhours.value AS DECIMAL ) END) as Total_work,
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

  WHERE t.status IN (#STATUSES#)
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

<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<form method="post" action="<?cs var:billing_info.href ?>" >
<div id="content" class="billing">
  <a href="<?cs var:billing_info.usermanual_href ?>" ><?cs var:billing_info.usermanual_title ?></a>
  <div id="messages" >
    <?cs each:item = billing_info.messages ?>
      <div class="message" ><?cs var:item ?></div>
    <?cs /each ?>
  </div>

  <table border="0" cellspacing="0" cellpadding="0" class="minorsection">
    <tr>
      <td colspan="2" >
            <div class="minorsection">
	    <div class="label" >Billing Status:</div>
              <label for="billable">Billable: </label>
              <input id="billable" name="billable" type="checkbox" checked="true" /> 

            &nbsp;&nbsp;|&nbsp;&nbsp;
              <label for="unbillable">Not Billable: </label>
              <input id="unbillable" name="unbillable" type="checkbox"  /> 
            </div>
            <div class="minorsection">
	    <div class="label" >Status:</div>
              <label for="new">New: </label>
              <input id="new" name="new" type="checkbox" checked="true" /> 
            &nbsp;&nbsp;|&nbsp;&nbsp;
              <label for="assigned">Assigned: </label>
              <input id="assigned" name="assigned" type="checkbox" checked="true" /> 
            &nbsp;&nbsp;|&nbsp;&nbsp;
              <label for="reopened">Reopened: </label>
              <input id="reopened" name="reopened" type="checkbox" checked="true" /> 
            &nbsp;&nbsp;|&nbsp;&nbsp;
              <label for="closed">Closed: </label>
              <input id="closed" name="closed" type="checkbox" checked="true" /> 
            </div>

      </td>
    </tr><tr class="minorsection">
      <td class="minorsectionleft" valign="top"><label for="startdate" >Start Date:</label></td>
      <td class="minorsectionright"><input id="startdate" name="startdate" type="text" /> or:<br />
          <label for="startbilling" >Choose an old billing date:</label><br />
          <select id="startbilling" name="startbilling" >
            <option value="" ></option>
              <?cs each:item = billing_info.billdates ?>
                <option value="<?cs var:item.value ?>" ><?cs var:item.text ?></option>
              <?cs /each ?>
          </select>
      </td>
    </tr><tr class="minorsection">
      <td class="minorsectionleft" valign="top"><label for="enddate" >End Date:</label>
      </td>
      <td class="minorsectionright">
          <input id="enddate" name="enddate" type="text" /> or:<br />
          <label for="endbilling" >Choose an old billing date:</label><br />
          <select id="endbilling" name="endbilling" >
            <option value="" ></option>
              <?cs each:item = billing_info.billdates ?>
                <option value="<?cs var:item.value ?>" ><?cs var:item.text ?></option>
              <?cs /each ?>
          </select>
      </td>
    </tr>
  </table>
  <ul id="reportlinks">
  <?cs each:report_group = billing_info.reports ?>
    <li><?cs var:report_group.title ?>
      <ul>
        <?cs each:report = report_group.reports ?>
          <li><a href="" onmouseover="linkify(this, '<?cs var:report.href ?>')"  >
            <?cs var:report.title ?>
          </a></li>     
       <?cs /each ?>
      </ul>
    </li>
  <?cs /each ?>
  </ul>
  <input type="submit" name="setbillingtime" value="Set Billing Time" onclick="return confirm('Are you sure that you want to create a billed date?')" />&nbsp;

</div>
</form>
<?cs include "footer.cs"?>
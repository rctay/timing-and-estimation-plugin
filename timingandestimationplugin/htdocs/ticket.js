(function(){
   function teAddEventListener(elem, evt, func, capture)
   {
      capture = capture || false;
      if (elem.addEventListener) elem.addEventListener(evt, func, capture);
      else elem.attachEvent('on'+evt, func);
      return func;
   }
   
// Function from: http://www.robertnyman.com/index.php?p=256
   function getElementsByClassName(className, tag, elm)
   {
      var testClass = new RegExp("(^|\\s)" + className + "(\\s|$)");
      var tag = tag || "*";
      var elm = elm || document;
      var elements = (tag == "*" && elm.all)? elm.all : elm.getElementsByTagName(tag);
      var returnElements = [];
      var current;
      var length = elements.length;
      for (var i=0; i<length; i++)
      {
	 current = elements[i];
	 if(testClass.test(current.className))
	 {
	    returnElements.push(current);
	 }
      }
      return returnElements;
   }
   

   function FloatToHoursMins(hours)
   {
      if (0 == hours) return hours;
      mins = Math.floor((hours - Math.floor(hours)) * 60);
      str = '';
      if (hours) str += Math.floor(hours) + 'h';
      if (mins)
      {
	 if (str) str += ' ';
	 str += mins + 'm';
      }
      return str;
   }
   
   function IntToYesNo(boolflag)
   {
      if (boolflag == '1')
	 return 'Yes';
      
      if (boolflag == '0')
	 return 'No';
      
      return boolflag;
   }
   
   
   InitBilling = function(){
      // Convert totalhours field to non-editable
      try
      {
	 var x = document.getElementById('totalhours');
	 x = x || document.getElementById('field-totalhours');
	 if (x)
	 {
	    var p = x.parentNode;
	    var n = document.createElement('span')
	       n.id = x.id;
	    n.appendChild(document.createTextNode(x.value));
	    p.removeChild(x);
	    p.appendChild(n);
	 }
      }
      catch (er) {}
      
      // Display yes/no in the summary
      // if we fail, then no harm done.
      try
      {
	 var b = document.getElementById('h_billable');
	 while (b)
	 {
	    if (!b.nextSibling) break;
	    b = b.nextSibling;
	    if (b.nodeName == 'TD')
	    {
	       b.innerHTML = IntToYesNo(b.innerHTML);
	       break;
	    }
	 }
      }
      catch (er) {}
  
  
      // Hide the Add Hours in the title table
      // if we fail, then no harm done.
      try
      {
	 var b = document.getElementById('h_hours');
	 b.firstChild.nodeValue = '';
	 b.nextSibling.nextSibling.firstChild.nodeValue = '';
      }
      catch (er) {}
      
      
      // Convert hours from float to hours minutes seconds
      // if we fail, then no harm done.
      try
      {
	 fields = Array('estimatedhours', 'totalhours');
	 for (i=0; i < 2; ++i) 
	 {
	    var b = document.getElementById('h_' + fields[i]);
	    while (b)
	    {
	       if (!b.nextSibling) break;
	       b = b.nextSibling;
	       if (b.nodeName == 'TD')
	       {
		  b.innerHTML = FloatToHoursMins(b.innerHTML);
		  break;
	       }
	    }
	 }
      }
      catch (er) {}
      
      // Convert all relevent ticket changes to hours/minutes
      // if we fail, then no harm done.
      try
      {
	 changes = getElementsByClassName('changes', 'ul', document.getElementById('changelog'));
	 for (i=0; i < changes.length; ++i)
	 {
	    change = changes[i];
	    for (j=0; j < change.childNodes.length; ++j)
	    {
	       li = change.childNodes[j];
	       if (li.nodeName != 'LI') continue;
	       // We look for a STRONG childNode
	       if (!li.firstChild 
		   || li.firstChild.nodeName != 'STRONG'
		   || !li.firstChild.firstChild
		   || li.firstChild.firstChild.nodeName != '#text')
	       {
		  continue;
	       }
	       
	       field = li.firstChild.firstChild.nodeValue;
	       if (field == 'billable')
	       {
		  for (k=1; k < li.childNodes.length; ++k)
		  {
		     if (li.childNodes[k].nodeName != 'EM'
			 || !li.childNodes[k].firstChild
			 || li.childNodes[k].firstChild.nodeName != '#text')
		     {
			continue;
		     }
		     li.childNodes[k].firstChild.nodeValue = IntToYesNo(li.childNodes[k].firstChild.nodeValue);
		  }
	       }
	       else if (field == 'hours'
			|| field == 'estimatedhours'
			|| field == 'totalhours')
	       {
		  for (k=1; k < li.childNodes.length; ++k)
		  {
		     if (li.childNodes[k].nodeName != 'EM'
			 || !li.childNodes[k].firstChild
			 || li.childNodes[k].firstChild.nodeName != '#text')
		     {
			continue;
		     }
		     li.childNodes[k].firstChild.nodeValue = FloatToHoursMins(li.childNodes[k].firstChild.nodeValue);
		  }
	       }
	    }
	 }
      }
      catch (er) {}
   }

   teAddEventListener(window, 'load', InitBilling)
})()


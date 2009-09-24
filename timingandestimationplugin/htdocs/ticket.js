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
      var neg = false;
      if(hours < 0){
	 neg = true;
	 hours *= -1;
      }
      mins = Math.floor((hours - Math.floor(hours)) * 60);
      str = neg ? '-' : '';
      if (hours) str += Math.floor(hours) + 'h';
      if (mins)	 str += ' ' + mins + 'm';
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
      /*  // Convert totalhours field to non-editable
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
      */

      // Display yes/no in the summary
      // if we fail, then no harm done.
      try
      {
	 var b = document.getElementById('h_billable');
	 do{ b = b.nextSibling; }while(b.nodeName != "TD");
	 b.innerHTML = IntToYesNo(b.innerHTML);
      }
      catch (er) {}
  
  
      // Hide the Add Hours in the title table
      // if we fail, then no harm done.
      try
      {
	 var b = document.getElementById('h_hours');
	 b.innerHTML = '';
	 do{ b = b.nextSibling; }while(b.nodeName != "TD");
	 b.innerHTML = '';
      }
      catch (er) {}
      
      
      // Convert hours from float to hours minutes seconds
      // if we fail, then no harm done.
      try
      {
	 fields = Array('estimatedhours', 'totalhours');
	 for (var i=0; i < 2; ++i) 
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
      try {
	 changes = getElementsByClassName('changes', 'ul', document.getElementById('changelog'));
	 var change, li;
	 for (var i=0; change = changes[i]; i++) {
	    for (var j=0, li = change.childNodes[j]; li = change.childNodes[j]; j++) {
	       handleChangeRow(li); 
	    }
	 }
      }
      catch (er) {}
   }

   handleChangeRow = function(li){
      var child, val, vals =[];
      if (li.nodeName != 'LI') return;
      // We look for a STRONG childNode
      // We also need to find any em's following the STRONG
      for(var i=0 ; child = li.childNodes[i] ; i++){
	 if (child.nodeName == 'STRONG'){
	    field = child.firstChild.nodeValue;
	    if(!(field == 'hours'
		 || field == 'estimatedhours'
		 || field == 'totalhours'))
	       return;
	 }
	 if (child.nodeName == 'EM'){
	    vals.push([child, child.firstChild.nodeValue])
	 } 
      }
      for(var i=0; val = vals[i] ; i++){
	 out = FloatToHoursMins(Number(val[1]))
	 //print(val[0]+'|'+ val[1] )
	 //print("#"+ out)
	 val[0].innerHTML = out
      }
      return vals;
   }

   teAddEventListener(window, 'load', InitBilling)
})()

Date.prototype.setISO8601 = function(dString){
  //from http://dansnetwork.com/2008/11/01/javascript-iso8601rfc3339-date-parser/
  var regexp = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))/;
  
  if (dString.toString().match(new RegExp(regexp))) {
    var d = dString.match(new RegExp(regexp));
    var offset = 0;
    
    this.setUTCDate(1);
    this.setUTCFullYear(parseInt(d[1],10));
    this.setUTCMonth(parseInt(d[3],10) - 1);
    this.setUTCDate(parseInt(d[5],10));
    this.setUTCHours(parseInt(d[7],10));
    this.setUTCMinutes(parseInt(d[9],10));
    this.setUTCSeconds(parseInt(d[11],10));
    if (d[12])
      this.setUTCMilliseconds(parseFloat(d[12]) * 1000);
    else
      this.setUTCMilliseconds(0);
    if (d[13] != 'Z') {
      offset = (d[15] * 60) + parseInt(d[17],10);
      offset *= ((d[14] == '-') ? -1 : 1);
      this.setTime(this.getTime() - offset * 60 * 1000);
    }
  }
  else {
    this.setTime(Date.parse(dString));
  }
  return this;
  };


function onClickOfADateElement(isoDate) {
  var commentTime = new Date();
  commentTime.setISO8601(isoDate);
  
  var now = new Date();
  var minutesDiff = (now - commentTime) / 1000 / 60;
  var fifteens = Math.floor(minutesDiff / 15);
  var remainder = minutesDiff % 15;
  var hours = (fifteens * 0.25) + ((remainder > 5) ? 0.25 : 0.0);
  $('#field-hours')[0].value = hours;
}



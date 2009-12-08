
//var linkify =
//(function(){
   String.prototype.trim =
      (function () {return this.replace(/^\s+/, "").replace(/\s+$/, "");});
   var invalidDate = new Date("invalid").toString();
   var billingfields= {};
   var statusfields = [];
   function dateToUnixEpoch(date){
      return Math.round(date.getTime()/1000) - (60 * date.getTimezoneOffset());
   }
   function makeDate(val) {
      try{
	 var d = Date.parse(val);
      }
      catch(e){
	 d = invalidDate;
      }
      if(!d || d.toString == invalidDate){
	 alert("You entered an invalid date: "+val);
	 return null;
      }
      return d;
   }
   function addBillingField( name /*optional type defaults to "textbox", optional flag status*/ ){
      var type = arguments.length >= 1 ? arguments[1] : "textbox";
      var status = arguments.length >= 2 ? arguments[2] : false;
      var getSet =
	 (function(){
	    var valueProp = "value";

	    if(type == "date"){
	       return function (/*optional value*/){
		  if(arguments.length == 0){
		     var d = makeDate(this.$()[valueProp]);
		     if (d) return dateToUnixEpoch(d);
		     else return null;
		  }
		  else{
		     var val = makeDate(arguments[0]);
		     if(!val){
			this.$()[valueProp] = null;
			return null;
		     }
		     this.$()[valueProp] = val;
		     return val;
		  }
	       };
	    }
	    //FOR EVERYTHING ELSE
	    if(type == "checkbox"){
	       valueProp = "checked";
	    }
	    return function (/*optional value*/){
	       //alert(name+" : "+type+" "+valueProp);
	       if(arguments.length == 0){
		  var val = (this.$())[valueProp];

		  if(typeof(val) == "string") val = val.trim();
		  if(val)return val;
		  return null;
	       }
	       else{
		  var val = arguments[0];
		  (this.$())[valueProp] = val;
		  return val;
	       }
	    };
	  })();
      billingfields[name] = {
	 "$" : function(){
	    return document.getElementById(name);
	 },
         getval : getSet,
	 setval : getSet
      };
      if (status){
	 statusfields.push({
	      name:name,
	      "$" : function(){
		  return document.getElementById(name);
	      },
	      getval : getSet,
	      setval : getSet
	 });
      }
   }

   addBillingField("billable", "checkbox");
   addBillingField("unbillable", "checkbox");
   addBillingField("startdate", "date");
   addBillingField("startbilling", "dateselect");
   addBillingField("enddate", "date");
   addBillingField("endbilling", "dateselect");


   var linkify = function ( atag, basehref ){
      var query = "";
      var haveAdded = false;
      function addToQuery(str){
	 query += haveAdded ? "&" : "?";
	 query += str;
	 haveAdded = true;
      }
      //billable logic
      addToQuery(billingfields["billable"].getval() || !(billingfields["unbillable"].getval())
		 ? "BILLABLE=1" : "BILLABLE=0");
      addToQuery(billingfields["unbillable"].getval() || !(billingfields["billable"].getval())
		 ? "UNBILLABLE=0" : "UNBILLABLE=1");

      for(var i=0, f = null ; f = statusfields[i] ; i++){
	 val = f.name.toUpperCase().replace("_","", "g").replace(" ","","g")+"=";
	 if(f.getval()){
	    val += f.name
	 }
	 addToQuery(val);
      }

      //startdate the date in the text box or the date in the dropdown or the first time
      startdate = billingfields["startdate"].getval() || billingfields["startbilling"].getval() || 0;
      addToQuery("STARTDATE="+startdate);
      //the date in the enddate text box or the date in the enddate billing box or real close to the end of integer unix epoch time
      // this will need a patch to continue working  past this point
      enddate = billingfields["enddate"].getval() || billingfields["endbilling"].getval() || 2000000000;
      addToQuery("ENDDATE="+enddate);

      atag.href = basehref+query;
   }
//})()

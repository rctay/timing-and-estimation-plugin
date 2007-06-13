//javascript:(function(){var filter = function (fn, list, thisObj) { var arr = []; for (var i = 0; i < list.length; i++) { if (fn.call(thisObj, list[i])) { arr.push(list[i]);return arr;var sum = 0; var tds = filter(function(td){return td.innerHTML =='None';document.getElementsByTagName('td'),this); for(var i = 0; i < tds.length; i++){sum += parseFloat(tds[i].parentNode.childNodes[5].innerHTML);alert('Total hours: ' + sum);})();
javascript:(
   function(){
      var filter = function (fn, list, thisObj) { 
	 var arr = []; 
	 for (var i = 0; i < list.length; i++) { 
	    if (fn.call(thisObj, list[i])) { 
	       arr.push(list[i]);
	    }
	 } 
	 return arr;
      }; 
      var sum = 0; 
      var tds = filter(function(td){
			  return td.innerHTML =='None';
		       },
		       document.getElementsByTagName('td'),this); 
      for(var i = 0; i < tds.length; i++){
	 sum += parseFloat(tds[i].parentNode.childNodes[5].innerHTML);
      } 
      alert('Total hours: ' + sum);
   }
)();

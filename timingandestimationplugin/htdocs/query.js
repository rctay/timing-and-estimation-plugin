(function(){
   function AddEventListener( elem, evt, func, capture){
      capture = capture || false;
      if(elem.addEventListener) elem.addEventListener( evt, func, capture);
      else elem.attachEvent('on'+evt, func);
      return func;
   };
   var InitQuery = function(){
      function createTableRow( numTds ){
	 var tr = document.createElement('tr');
	 var td = document.createElement('td');
	 td.style.backgroundColor="#EEF";
	 for(var i=0 ; i < numTds ; i++){
	    tr.appendChild(td.cloneNode(true));
	 }
	 return tr;
      }

      var _tbls = document.getElementsByTagName('table');
      var tbls = [], tbl, cell;
      // filter so that we only get ticket listing tables
      for(var i=0 ; tbl = _tbls[i] ; i++ ){
	 if(tbl.className == 'listing tickets') tbls.push(tbl);
      }

      // find numerical columns
      tbl = tbls[0];
      
      var cells = tbl.tBodies[0].rows[0].cells;
      var cellIdxs = [], columnNames = {};
      for(var i=0 ; cell = cells[i] ; i++ ){
	 if(cells[i].textContent!="" && !isNaN(Number(cells[i].textContent))){
	    cellIdxs.push(i);
	    if(tbl && tbl.tHead.rows.length > 0)
	       columnNames[i] = tbl.tHead.rows[0].cells[i].textContent;
	 }
      }

      // total the numerical columns and add a total row to each table
      var totals, total_totals =[], idx;
      for(var i=0 ; tbl = tbls[i] ; i++ ){
	 totals = [];
	 for(var k=0 ; row = tbl.tBodies[0].rows[k] ; k++){
	    for(var j=0 ; idx = cellIdxs[j] ; j++){
	       if(totals[idx] == null) totals[idx] = 0;
	       if(total_totals[idx] == null) total_totals[idx] = 0;
	       if(row.cells[idx].textContent!="" && !isNaN(Number(row.cells[idx].textContent))){
		  var val = Number(row.cells[idx].textContent);
		  total_totals[idx] += val
                  totals[idx] += val;
	       }
	    }
	 }
	 if(tbl.tBodies[0].rows.length > 0){
	    var tr = createTableRow(tbl.tBodies[0].rows[0].cells.length);
	    for(var j=0 ; idx = cellIdxs[j] ; j++){
	       tr.cells[idx].appendChild(document.createTextNode(totals[idx])); 
	    }
	    tbl.tBodies[0].appendChild(tr);
	 }
      }
      // If we are grouping by things, we are going to want to add a complete total to the bottom
      if(tbls.length > 1){
	 var totalHtml = document.createElement('div');
	 totalHtml.style.backgroundColor="#EEF";
	 for(var j=0 ; idx = cellIdxs[j] ; j++){
	    totalHtml.appendChild(document.createTextNode("Total "+columnNames[idx]+": "+total_totals[idx])); 
	    totalHtml.appendChild(document.createElement('br'));
	 }
	 tbls[0].parentNode.appendChild(totalHtml);
      }
   }
   AddEventListener(window, 'load', InitQuery)
})()

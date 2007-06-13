(function(){
   function AddEventListener( elem, evt, func, capture){
      capture = capture || false;
      if(elem.addEventListener) elem.addEventListener( evt, func, capture);
      else elem.attachEvent('on'+evt, func);
      return func;
   };
   InitBilling = function(){
      var x = document.getElementById('totalhours');
      x = x || document.getElementById('field-totalhours');
      if(x){
	 var p = x.parentNode;
	 var n = document.createElement('span');
	 n.id = x.id;
	 n.innerHTML = x.value;
	 p.removeChild(x);
	 p.appendChild(n);
      }
   }
   AddEventListener(window, 'load', InitBilling)
})()

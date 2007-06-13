import re
from trac.log import logger_factory
from trac.core import *
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.chrome import add_stylesheet, add_script, \
     INavigationContributor, ITemplateProvider
from trac.web.href import Href

class TicketWebUiAddon(Component):
    implements(INavigationContributor)
    
    def __init__(self):
        pass
    
     # INavigationContributor methods
    def get_active_navigation_item(self, req):
    
        if re.search('ticket', req.path_info):
            return "ticket-addon"
        else:
            return ""

    def get_navigation_items(self, req):
        if re.search('ticket', req.path_info):
            yield 'mainnav', "ticket-addon", \
                  Markup("""<script language="javascript" type="text/javascript">
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
                      var n = document.createElement('span')
                      n.id = x.id;
                      n.innerHTML = x.value
                      p.removeChild(x);
                      p.appendChild(n);
                    }
                  }
                  AddEventListener(window, 'load', InitBilling)
                  </script>""")

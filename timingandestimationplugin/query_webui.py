import re
from trac.log import logger_factory
from trac.core import *
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.chrome import add_stylesheet, add_script, \
     INavigationContributor, ITemplateProvider
from trac.web.href import Href

class QueryWebUiAddon(Component):
    implements(INavigationContributor)
    
    def __init__(self):
        pass
    
     # INavigationContributor methods
    def get_active_navigation_item(self, req):
    
        if re.search('query', req.path_info):
            return "query-addon"
        else:
            return ""

    def get_navigation_items(self, req):
        src = req.href.chrome("Billing/query.js")
        if re.search('query', req.path_info):
            yield 'mainnav', "query-addon", \
                  Markup("""<script language="javascript" type="text/javascript" src="%s"></script>"""%src)

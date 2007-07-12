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
            add_script(req, 'Billing/ticket.js')
            yield 'mainnav', "ticket-addon", ""

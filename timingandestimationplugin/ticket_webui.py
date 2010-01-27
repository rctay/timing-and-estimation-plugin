import re
from trac.web.api import ITemplateStreamFilter
from trac.log import logger_factory
from trac.core import *
from genshi.builder import tag
from trac.web import IRequestHandler
from trac.util import Markup
from trac.web.href import Href
from genshi.filters.transform import Transformer
from trac.web.api import ITemplateStreamFilter


class TicketWebUiAddon(Component):
    implements(ITemplateStreamFilter)
    
    def __init__(self):
        pass

    # ITemplateStreamFilter
    def filter_stream(self, req, method, filename, stream, data):
        self.log.debug("TicketWebUiAddon executing") 
        if not filename == 'ticket.html':
            #self.log.debug("TicketWebUiAddon not emitting ticket javascript because we are not on ticket.html")
            return stream
        stream = stream | Transformer('//div[@id="banner"]').before(
            tag.script(type="text/javascript", 
                       src=req.href.chrome("Billing", "ticket.js"))()
            )
        return stream

"""
Copyright (C) 2010, Tay Ray Chuan
"""

from trac.core import *

from pkg_resources import resource_filename
from trac.web.api import IRequestFilter
from trac.web.chrome import ITemplateProvider, add_script

class TicketStopwatch(Component):
    implements(IRequestFilter, ITemplateProvider)
    
    # IRequestFilter
    def pre_process_request(self, req, handler):
        return handler
        
    def post_process_request(self, req, template, data, content_type):
        if req.path_info.startswith('/ticket/'):
            add_script(req, 'stopwatch/stopwatch.js')
                                    
        return template, data, content_type

    # ITemplateProvider
    def get_htdocs_dirs(self):
        return [('stopwatch', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []

import re
import dbhelper
from trac import util
from trac.web.api import ITemplateStreamFilter
from trac.core import *
from genshi.core import *
from genshi.builder import tag
from genshi.filters.transform import Transformer

import sys 
if sys.version_info < (2, 4, 0): 
    from sets import Set as set

def split_stream(stream):
    """splits the stream based on toplevel START / END tags"""
    cl = []
    res = []
    num_start=0
    for kind, data, pos in stream:
        cl.append((kind, data, pos))
        if kind == Stream.START:
            num_start = num_start+1
        elif kind == Stream.END:
            num_start = num_start-1
            if num_start == 0:
                res.append(Stream(cl))
                cl=[]
    if cl != []:
        res.append(Stream(cl))
    return res


class RowFilter(object):
    """A genshi filter that operates on table rows, completely hiding any that
    are in the billing_reports table."""

    def __init__(self, comp):
        self.component = comp
        rows = dbhelper.get_all(comp, "SELECT id FROM custom_report")[1]
        if rows:
            self.billing_reports = set([x[0] for x in rows])
        else:
            self.billing_reports = set()
        self.component.log.debug('self.billing_reports= %r' % self.billing_reports)

    def __call__(self, row_stream):
        #stream = Stream(list(row_stream))
        def tryInt(v):
            try:
                return int(v)
            except:
                return None
        streams = split_stream(row_stream)
        #report_urls = [tryInt(i.get('href').split('/')[-1]) for i in stream.select('td[@class="report"]/a/@href')]
        #self.component.log.debug("ReportRowFilter: #%s#,  %r" % (len(streams), list(report_urls)))
        for stream in streams:
            show_row = True
            try:
                report_url = stream.select('td[@class="report"]/a/@href').render()
                id = tryInt(report_url.split('/')[-1])
                self.component.log.debug("Report row filter: about to filter: %s not in %s : %s" % (id, self.billing_reports,  not id in self.billing_reports) )
                show_row = not id in self.billing_reports 
            except Exception, e:
                self.component.log.exception("Report row filter failed")
                show_row = True #Dont Hide Error Rows?
            if show_row:
                for kind,data,pos in stream:
                    yield kind,data,pos

# This can go away once they fix http://genshi.edgewall.org/ticket/136
# At that point we should use Transformer.filter
class FilterTransformation(object):
    """Apply a normal stream filter to the selection. The filter is called once
    for each contiguous block of marked events."""

    def __init__(self, filter):
        """Create the transform.

        :param filter: The stream filter to apply.
        """
        self.filter = filter

    def __call__(self, stream):
        """Apply the transform filter to the marked stream.

        :param stream: The marked event stream to filter
        """
        def flush(queue):
            if queue:
                for event in self.filter(queue):
                    yield event
                del queue[:]

        queue = []
        for mark, event in stream:
            if mark:
                queue.append(event)
            else:
                for e in flush(queue):
                    yield None,e
                yield None,event
        for event in flush(queue):
            yield None,event

class ReportsFilter(Component):
    """Remove all billing reports from the reports list."""
    implements(ITemplateStreamFilter)

    def match_stream(self, req, method, filename, stream, data):
        return filename == 'report_view.html'

    def filter_stream(self, req, method, filename, stream, data):
        return stream | Transformer(
            '//table[@class="listing reports"]/tbody/tr'
            ).apply(FilterTransformation(RowFilter(self)))


#@staticmethod
def disable_field(field_stream):
    value = Stream(field_stream).select('@value').render()
    
    for kind,data,pos in tag.span(value, id="field-totalhours").generate():
        yield kind,data,pos

class TotalHoursFilter(Component):
    """Disable editing of the Total Hours field so that we don't need Javascript."""
    implements(ITemplateStreamFilter)

    def match_stream(self, req, method, filename, stream, data):
        self.log.debug("matching: ticket.html")
        return filename == 'ticket.html'

    def filter_stream(self, req, method, filename, stream, data):
        return stream | Transformer(
            '//input[@id="field-totalhours" and @type="text" and @name="field_totalhours"]'
            ).apply(FilterTransformation(disable_field))





class TimeClickFilter(Component):
    """Add a javascript onclick button to add the time since the change into the add hours box """
    implements(ITemplateStreamFilter)
    
    def match_stream(self, req, method, filename, stream, data):
        self.log.debug("matching: ticket.html")
        return filename == 'ticket.html'

    def filter_stream(self, req, method, filename, stream, data):
        if not self.env.config.getbool('timingandestimationplugin','show_add_time_buttons'):
            return stream
        def add_time_click(field_stream):
            time = Stream(field_stream).select('@title').render()
            time = time.split(" ")[0] # get the time out of the title
            #render the guts of the h3 without changes
            for kind,data,pos in field_stream:
                yield kind,data,pos
            #create the button tag that to add hours
            btn = tag.input(None, type='submit', title="add time elapsed since this comment", value="Add Time", time=time, onclick="onClickOfADateElement(this.getAttribute('time'));return false;")
            #create a div with the class that all the other buttons have
            new_stream = tag.div(btn, **{"class":"inlinebuttons"})
            #output new div/button
            for kind,data,pos in new_stream:
                yield kind,data,pos                    

        return stream | Transformer(
            # we want the text and the nodes so that we can insert at the end
            '//h3[@class="change"]/*|//h3[@class="change"]/text()'
            ).apply(FilterTransformation(add_time_click))






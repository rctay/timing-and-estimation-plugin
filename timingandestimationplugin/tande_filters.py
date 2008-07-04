from trac.web.api import ITemplateStreamFilter
from trac.core import *
from genshi.core import *
from genshi.builder import tag
from genshi.filters.transform import Transformer

class RowFilter(object):
    """A genshi filter that operates on table rows, completely hiding any that
    are in the billing_reports table."""

    def __init__(self, comp):
        self.component = comp
        cur = comp.env.get_db_cnx().cursor()
        try:
            cur.execute("SELECT id FROM custom_report")
            self.billing_reports = set([x[0] for x in cur.fetchall()])
        except Exception, e:
            # if we can't get the billing reports (e.g. the
            # TimingAndEstimationPlugin isn't installed), silently continue
            # without hiding anything.
            self.billing_reports = set()
        self.component.log.debug('self.billing_reports= %r' % self.billing_reports)

    def __call__(self, row_stream):
        events = list(row_stream)
        report_url = Stream(events) \
                        .select('td[@class="report"]/a/@href').render()
        id = int(report_url.split('/')[-1])

        if not id in self.billing_reports:
            for kind,data,pos in Stream(events):
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






#!/usr/bin/env python

# trac-post-commit-hook
# ----------------------------------------------------------------------------
# Copyright (c) 2004 Stephen Hansen 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ----------------------------------------------------------------------------

# This Subversion post-commit hook script is meant to interface to the
# Trac (http://www.edgewall.com/products/trac/) issue tracking/wiki/etc 
# system.
# 
# It should be called from the 'post-commit' script in Subversion, such as
# via:
#
# REPOS="$1"
# REV="$2"
# LOG=`/usr/bin/svnlook log -r $REV $REPOS`
# AUTHOR=`/usr/bin/svnlook author -r $REV $REPOS`
# TRAC_ENV='/somewhere/trac/project/'
# TRAC_URL='http://trac.mysite.com/project/'
#
# /usr/bin/python /usr/local/src/trac/contrib/trac-post-commit-hook \
#  -p "$TRAC_ENV"  \
#  -r "$REV"       \
#  -u "$AUTHOR"    \
#  -m "$LOG"       \
#  -s "$TRAC_URL"
#
# It searches commit messages for text in the form of:
#   command #1
#   command #1, #2
#   command #1 & #2 
#   command #1 and #2
#
# You can have more then one command in a message. The following commands
# are supported. There is more then one spelling for each command, to make
# this as user-friendly as possible.
#
#   closes, fixes
#     The specified issue numbers are closed with the contents of this
#     commit message being added to it. 
#   references, refs, addresses, re 
#     The specified issue numbers are left in their current status, but 
#     the contents of this commit message are added to their notes. 
#
# A fairly complicated example of what you can do is with a commit message
# of:
#
#    Changed blah and foo to do this or that. Fixes #10 and #12, and refs #12.
#
# This will close #10 and #12, and add a note to #12.

#
# Changes for the Timing and Estimation plugin
#
# "Blah refs #12 (1)" will add 1h to the spent time for issue #12
# "Blah refs #12 (spent 1)" will add 1h to the spent time for issue #12
#
# As above it is possible to use complicated messages:
#
# "Changed blah and foo to do this or that. Fixes #10 (1) and #12 (2), and refs #13 (0.5)."
#
# This will close #10 and #12, and add a note to #13 and also add 1h spent time to #10,
# add 2h spent time to #12 and add 30m spent time to #13.
#
# Note that:
#     spent, sp or simply nothing may be used for spent
#     ' ', ',', '&' or 'and' may be used between spent
#

import re
import os
import sys
import time 

from trac.env import open_environment
from trac.ticket.notification import TicketNotifyEmail
from trac.ticket import Ticket
from trac.ticket.web_ui import TicketModule
# TODO: move grouped_changelog_entries to model.py
from trac.util.text import to_unicode
from trac.web.href import Href

# f = open ("/tmp/commithook.log","w")
# f.write("Begin Log\n")
# f.close()
# def log (s):
#     f = open ("/tmp/commithook.log","a")
#     f.write(s);
#     f.write("\n")
#     f.close()
    
try:
    from optparse import OptionParser
except ImportError:
    try:
        from optik import OptionParser
    except ImportError:
        raise ImportError, 'Requires Python 2.3 or the Optik option parsing library.'

parser = OptionParser()
parser.add_option('-e', '--require-envelope', dest='env', default='',
                  help='Require commands to be enclosed in an envelope. If -e[], '
                       'then commands must be in the form of [closes #4]. Must '
                       'be two characters.')
parser.add_option('-p', '--project', dest='project',
                  help='Path to the Trac project.')
parser.add_option('-r', '--revision', dest='rev',
                  help='Repository revision number.')
parser.add_option('-u', '--user', dest='user',
                  help='The user who is responsible for this action')
parser.add_option('-m', '--msg', dest='msg',
                  help='The log message to search.')
parser.add_option('-c', '--encoding', dest='encoding',
                  help='The encoding used by the log message.')
parser.add_option('-s', '--siteurl', dest='url',
                  help='The base URL to the project\'s trac website (to which '
                       '/ticket/## is appended).  If this is not specified, '
                       'the project URL from trac.ini will be used.')

(options, args) = parser.parse_args(sys.argv[1:])

if options.env:
    leftEnv = '\\' + options.env[0]
    rghtEnv = '\\' + options.env[1]
else:
    leftEnv = ''
    rghtEnv = ''

andPattern = '(?:[ ]*(?:[, &]|[ ]and[ ])[ ]*)'
timePattern = '(?:\((?:(?:(?:spent|sp)[ ])?[0-9]*(?:\.[0-9]+)?)?(?:\))?)?'
commandPattern = re.compile(leftEnv + r'(?P<action>[A-Za-z]*).?(?P<ticket>#[0-9]+[ ]*' + timePattern + '(?:' + andPattern + '#[0-9]+.?' + timePattern + '.?)*)' + rghtEnv)
ticketSplitPattern = re.compile(r'(#[0-9]+[ ]*' + timePattern + ')')
ticketPattern = re.compile(r'(?:#([0-9]+)[ ]*(?:\((?:(?:(?:spent|sp)[ ])?([0-9]*(?:\.[0-9]*)?))?\))?)')

class CommitHook:
    _supported_cmds = {'close':      '_cmdClose',
                       'closed':     '_cmdClose',
                       'closes':     '_cmdClose',
                       'fix':        '_cmdClose',
                       'fixed':      '_cmdClose',
                       'fixes':      '_cmdClose',
                       'addresses':  '_cmdRefs',
                       're':         '_cmdRefs',
                       'references': '_cmdRefs',
                       'refs':       '_cmdRefs',
                       'see':        '_cmdRefs'}

    def __init__(self, project=options.project, author=options.user,
                 rev=options.rev, msg=options.msg, url=options.url,
                 encoding=options.encoding):
        msg = to_unicode(msg, encoding)
        self.author = author
        self.rev = rev
        self.msg = "(In [%s]) %s" % (rev, msg)
        self.now = int(time.time()) 
        self.env = open_environment(project)
        if url is None:
            url = self.env.config.get('project', 'url')
        self.env.href = Href(url)
        self.env.abs_href = Href(url)

        cmdGroups = commandPattern.findall(msg)
        for cmd, tkts in cmdGroups:
            funcname = CommitHook._supported_cmds.get(cmd.lower(), '')
            if funcname:
                func = getattr(self, funcname)
                tickets = ticketSplitPattern.findall(tkts)
                for ticket in tickets:
                    ticketAndTimes = ticketPattern.findall(ticket)
                    for tkt_id, spent in ticketAndTimes:
                        try:
                            db = self.env.get_db_cnx()

                            ticket = Ticket(self.env, int(tkt_id), db)
                            func(ticket)

                            # determine sequence number... 
                            cnum = 0
                            tm = TicketModule(self.env)
                            for change in tm.grouped_changelog_entries(ticket, db):
                                if change['permanent']:
                                    cnum += 1

                            self._setTimeTrackerFields(ticket, spent)
                            ticket.save_changes(self.author, self.msg, self.now, db, cnum+1)
                            db.commit()
                            
                            tn = TicketNotifyEmail(self.env)
                            tn.notify(ticket, newticket=0, modtime=self.now)
                        except Exception, e:
                            # import traceback
                            # traceback.print_exc(file=sys.stderr)
                            print>>sys.stderr, 'Unexpected error while processing ticket ' \
                                               'ID %s: %s' % (tkt_id, e)

    def _cmdClose(self, ticket):
        ticket['status'] = 'closed'
        ticket['resolution'] = 'fixed'

    def _cmdRefs(self, ticket):
        pass

    def _setTimeTrackerFields(self, ticket, spent):
        if (spent != ''):
            spentTime = float(spent)
            if (ticket.values.has_key('hours')):
                ticket['hours'] = str(spentTime)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print "For usage: %s --help" % (sys.argv[0])
    else:
        CommitHook()

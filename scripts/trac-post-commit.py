#!/usr/bin/env python
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
#
# /usr/bin/python /usr/local/src/trac/contrib/trac-post-commit-hook \
#  -p "$TRAC_ENV" -r "$REV"
#
# (all the other arguments are now deprecated and not needed anymore)
#
# It searches commit messages for text in the form of:
#   command #1
#   command #1, #2
#   command #1 & #2 
#   command #1 and #2
#
# Instead of the short-hand syntax "#1", "ticket:1" can be used as well, e.g.:
#   command ticket:1
#   command ticket:1, ticket:2
#   command ticket:1 & ticket:2 
#   command ticket:1 and ticket:2
#
# In addition, the ':' character can be omitted and issue or bug can be used
# instead of ticket.
#
# You can have more then one command in a message. The following commands
# are supported. There is more then one spelling for each command, to make
# this as user-friendly as possible.
#
#   close, closed, closes, fix, fixed, fixes
#     The specified issue numbers are closed with the contents of this
#     commit message being added to it. 
#   references, refs, addresses, re, see 
#     The specified issue numbers are left in their current status, but 
#     the contents of this commit message are added to their notes. 
#
# A fairly complicated example of what you can do is with a commit message
# of:
#
#    Changed blah and foo to do this or that. Fixes #10 and #12, and refs #12.
#
# This will close #10 and #12, and add a note to #12.

import re
import os
import sys
from datetime import datetime 

from trac.env import open_environment
from trac.ticket.notification import TicketNotifyEmail
from trac.ticket import Ticket
from trac.ticket.web_ui import TicketModule
# TODO: move grouped_changelog_entries to model.py
from trac.util.text import to_unicode
from trac.util.datefmt import utc
from trac.versioncontrol.api import NoSuchChangeset

logfile = "/var/trac/commithook.log"
LOG = False

if LOG:
    f = open (logfile,"w")
    f.write("Begin Log\n")
    f.close()
    def log (s, *params):http://www.bestbuy.com/site/olspage.jsp?skuId=8400517&st=lg+lcd&type=product&id=1179877503368
        f = open (logfile,"a")
        f.write(s % params);
        f.write("\n")
        f.close()
else:
    def log (s, *params):
        pass

from optparse import OptionParser

parser = OptionParser()
depr = '(not used anymore)'
parser.add_option('-e', '--require-envelope', dest='envelope', default='',
                  help="""
Require commands to be enclosed in an envelope.
If -e[], then commands must be in the form of [closes #4].
Must be two characters.""")
parser.add_option('-p', '--project', dest='project',
                  help='Path to the Trac project.')
parser.add_option('-r', '--revision', dest='rev',
                  help='Repository revision number.')
parser.add_option('-u', '--user', dest='user',
                  help='The user who is responsible for this action '+depr)
parser.add_option('-m', '--msg', dest='msg',
                  help='The log message to search '+depr)
parser.add_option('-c', '--encoding', dest='encoding',
                  help='The encoding used by the log message '+depr)
parser.add_option('-s', '--siteurl', dest='url',
                  help=depr+' the base_url from trac.ini will always be used.')

(options, args) = parser.parse_args(sys.argv[1:])

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

ticket_prefix = '(?:#|(?:ticket|issue|bug)[: ]?)'
time_pattern = r'[ ]?(?:\((?:(?:spent|sp)[ ]?)?(-?[0-9]*(?:\.[0-9]+)?)\))?'
ticket_reference = ticket_prefix + '[0-9]+'+time_pattern
support_cmds_pattern = '|'.join(_supported_cmds.keys())
ticket_command =  (r'(?P<action>(?:%s))[ ]*'
                   '(?P<ticket>%s(?:(?:[, &]*|[ ]?and[ ]?)%s)*)' %
                   (support_cmds_pattern,ticket_reference, ticket_reference))
command_re = re.compile(ticket_command)
ticket_re = re.compile(ticket_prefix + '([0-9]+)')


if options.envelope:
    ticket_command = r'\%s%s\%s' % (options.envelope[0], ticket_command,
                                    options.envelope[1])
    
command_re = re.compile(ticket_command)
ticket_re = re.compile(ticket_prefix + '([0-9]+)'+time_pattern)

class CommitHook:

    def init_env(self, project):
        self.env = open_environment(project)
        

    def __init__(self, project=options.project, author=options.user,
                 rev=options.rev, url=options.url):
        self.init_env( project )
        
        repos = self.env.get_repository()
        repos.sync()
        # Instead of bothering with the encoding, we'll use unicode data
        # as provided by the Trac versioncontrol API (#1310).
        try:
            chgset = repos.get_changeset(rev)
        except NoSuchChangeset:
            return # out of scope changesets are not cached
        self.author = chgset.author
        self.rev = rev
        self.msg = "(In [%s]) %s" % (rev, chgset.message)
        self.now = datetime.now(utc)

        cmd_groups = command_re.findall(self.msg)
        log ("cmd_groups:%s", cmd_groups)
        tickets = {}
        for cmd, tkts, xxx1, xxx2 in cmd_groups:
            log ("cmd:%s, tkts%s ", cmd, tkts)
            funcname = _supported_cmds.get(cmd.lower(), '')
            if funcname:
                for tkt_id, spent in ticket_re.findall(tkts):
                    func = getattr(self, funcname)
                    lst = tickets.setdefault(tkt_id, [])
                    lst.append([func, spent])
                    

        for tkt_id, vals in tickets.iteritems():
            log ("tkt_id:%s, vals%s ", tkt_id, vals)
            spent_total = 0.0
            try:
                db = self.env.get_db_cnx()
                
                ticket = Ticket(self.env, int(tkt_id), db)
                for (cmd, spent) in vals:
                    cmd(ticket)
                    if spent:
                        spent_total += float(spent)

                # determine sequence number... 
                cnum = 0
                tm = TicketModule(self.env)
                for change in tm.grouped_changelog_entries(ticket, db):
                    if change['permanent']:
                        cnum += 1
                if spent_total:
                    self._setTimeTrackerFields(ticket, spent_total)
                ticket.save_changes(self.author, self.msg, self.now, db, cnum+1)
                db.commit()

                tn = TicketNotifyEmail(self.env)
                tn.notify(ticket, newticket=0, modtime=self.now)
            except Exception, e:
                # import traceback
                # traceback.print_exc(file=sys.stderr)
                log('Unexpected error while processing ticket ' \
                                   'ID %s: %s' % (tkt_id, e))
                print>>sys.stderr, 'Unexpected error while processing ticket ' \
                                   'ID %s: %s' % (tkt_id, e)
            

    def _cmdClose(self, ticket):
        ticket['status'] = 'closed'
        ticket['resolution'] = 'fixed'

    def _cmdRefs(self, ticket):
        pass

    def _setTimeTrackerFields(self, ticket, spent):
        log ("Setting ticket:%s spent: %s", ticket, spent)
        if (spent != ''):
            spentTime = float(spent)
            if (ticket.values.has_key('hours')):
                ticket['hours'] = str(spentTime)
                

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print "For usage: %s --help" % (sys.argv[0])
        print
        print "Note that the deprecated options will be removed in Trac 0.12."
    else:
        CommitHook()


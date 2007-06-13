user_manual_title = "Timing and Estimation Plugin User Manual"
user_manual_version = 8
user_manual_wiki_title = "TimingAndEstimationPluginUserManual"
user_manual_content = """
[[TOC]]
= Timing and Estimation Plugin User Manual =
[http://trac-hacks.org/wiki/TimingAndEstimationPlugin TimingAndEstimationPlugin on TracHacks] | [http://trac-hacks.org/report/9?COMPONENT=TimingAndEstimationPlugin Open Tickets] | [http://trac-hacks.org/newticket?component=TimingAndEstimationPlugin&owner=bobbysmith007 New Ticket]  | 
[http://trac-hacks.org/browser/timingandestimationplugin/trunk Web Browsable Source Code]

== Abstract Design Goal ==
My goal in writing this plugin was to use as much of the existing structure as possible (therefore not needing to add extra structure that might make maintainability difficult).  The largest downside I have found to this is that there is no way to attach more permissions to anything.

== Custom Ticket Fields ==
In adhering to our design goal, rather than creating a new ticket interface, I create some custom fields and a small daemon to watch over them.  

=== Fields: ===
 * '''Hours to Add''' This field functions as a time tracker.  When you add hours to it , those hours get added to the total hours field.  The person  who made the change is there fore credited with the hours spent on it.
 * '''Total Hours''' This field is the total number of hours that have been added to the project. This has been made uneditable by including javascript which replaces the input box with a span containing its value
   * Reports might not agree with each other if this is manually edited (which is possible if you disable javascript).
 * '''Is this billable?''' An extra flag on tickets so that they can be marked as billable / not billable.
 * '''Estimated Hours''' a field that contains the estimated amount of work
=== Future Fields ===
 * '''Ticket Rate''' The ability to attach a cost per hour or total amount to an individual ticket

== Management Page ==
This page provide a small interface for querying the tickets and adding a bill date at the current time.  
This interface mostly just gives you links that match the interface to open any of the give reports,
providing it the correct set of input parameters

=== Set Bill Date ===

This button will add now as a bill date.  This is mostly to make it
easier to select the last time you billed.  This would allow you to
set a ticket as having been billed at a given time while others have
not, and accurately get the correct billing information for all
tickets.

== Reports ==
We provide a few different reports for querying different types of data:
    * '''Billing Reports''' Currently the billing reports are the only time based reports, and are therefore useful for getting an estimate what tickets had times (and totals), and which developers spent their time where.
       * Ticket Work Summary
       * Milestone Work Summary
       * Developer Work Summary
    * '''Ticket/Hour Reports''' These reports are useful for reviewing estimates on a large scale or getting an idea of the project at large.  These reports currently ignore the time.
       * Ticket Hours
       * Ticket Hours with Description 
       * Ticket Hours Grouped By Component
       * Ticket Hours Grouped By Component with Description
       * Ticket Hours Grouped By Milestone
       * Ticket Hours Grouped By Milestone with Description

== Future Improvements ==
 * [http://trac-hacks.org/wiki/TimingAndEstimationPlugin See tickets] at the [http://trac-hacks.org/wiki/TimingAndEstimationPlugin project trac]
 * Would like to suggest a couple of interfaces to Trac project, and perhaps write an implementation for them.
   * ''' ICustomTicketFieldProvider ''' This should allow a plugin to provide a custom field with the ability to add html attributes and specify at least the tag name. (hopefully with a full template) This should hopefully also allow these provided custom controls to set permissions causing them to not render or to not editable.
   * ''' ICustomReportProvider ''' This allows custom reports to be provided in a way that permissions can be enforced on them. 
 * work with advise and feedback from the user community to make this Plugin do this job adequately

"""

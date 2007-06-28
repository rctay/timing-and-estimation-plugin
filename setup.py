#!/usr/bin/env python

from setuptools import setup

PACKAGE = 'timingandestimationplugin'

setup(name=PACKAGE,
      description='Plugin to make Trac support time estimation and tracking',
      keywords='trac plugin estimation timetracking',
      version='0.4.3',
      url='http://trac-hacks.org/wiki/TimingAndEstimationPlugin',
      license='http://www.opensource.org/licenses/mit-license.php',
      author='Russ Tyndall at Acceleration.net',
      author_email='russ@acceleration.net',
      long_description="""
      This Trac 0.11 plugin provides support for Time estimation and tracking.

      See http://trac-hacks.org/wiki/TimingAndEstimationPlugin for details.
      """,
      packages=[PACKAGE],
      package_data={PACKAGE : ['templates/*.cs', 'htdocs/*', 'migrate/*.py']},
      entry_points={'trac.plugins': '%s = %s' % (PACKAGE, PACKAGE)})


#### AUTHORS ####
## Primary Author:
## Russell Tyndall
## Acceleration.net
## russ@acceleration.net
## trac-hacks user: bobbysmith007

##

## Alessio Massaro
## trac-hacks user: masariello
## Helped Get Reports working in postgres
## and started moving toward generic work 
## rather than hours

## kkurzweil@lulu.com
## helped postegresql db backend compatiblity

## jonas
## made it so that base_url was unnecessary


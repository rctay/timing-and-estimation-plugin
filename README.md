Stopwatch widget for timingandestimationplugin
==============================================

Summary
-------

The TaE maintainer, Russ, has been very positive about this widget. At the time of writing, he is working to include it in the main TaE repo/distribution.

In the meantime, you can get this in two ways:

1. The 'master' branch, which is a ready-for-install replacement of TaE 0.11.

2. The 'export' branch, which has adds/replaces files in TaE.

Files
-----

	timingandestimationplugin/api.py                   |    1 +
	.../htdocs/StopwatchControls.js                    |   52 +++++++++++++
	.../htdocs/StopwatchDisplay.js                     |   78 ++++++++++++++++++++
	timingandestimationplugin/htdocs/Toggler.js        |   55 ++++++++++++++
	timingandestimationplugin/htdocs/stopwatch.js      |   44 +++++++++++
	timingandestimationplugin/stopwatch.py             |   32 ++++++++
	6 files changed, 262 insertions(+), 0 deletions(-)

/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var toggler, stopwatch;

	/*
 	 * add buttons to control the stopwatch
	 *
	 * Button 'flow' has states: start -> stop <-> continue
	 * Button 'reset' has state: reset
	 */
	Stopwatch = function() {
		/* the stopwatch (looks like 00:00:00) */
		var field_hour = $('<span>00</span>');
		var field_min = $('<span>00</span>');
		var field_sec = $('<span>00</span>');

		field_hour = field_hour[0].firstChild;
		field_min = field_min[0].firstChild;
		field_sec = field_sec[0].firstChild;

		var interval_id, interval_func, interval_params;
		var interval_func = function(p) {
			if (++p.ms>=10) {
				p.ms = 0;
				p.s++;
				field_sec.nodeValue = p.s < 10 ? '0'+p.s : p.s;
			}
			if (p.s>=60) {
				p.s = 0;
				p.m++;
				field_min.nodeValue = p.m < 10 ? '0'+p.m : p.m;
			}
			if (p.m>=60) {
				p.m = 0;
				p.h++;
				field_hour.nodeValue = p.h < 10 ? '0'+p.h : p.h;
			}
		};

		return {
			interval_params: interval_params,

			init: function(p_stopwatch) {
				p_stopwatch
					.append(field_hour)
					.append(':')
					.append(field_min)
					.append(':')
					.append(field_sec);
			},
			pause_stopwatch_display: function() {
				clearInterval(interval_id);
				interval_id = null;

				StopwatchControls.btn_flow.text('Continue');
				StopwatchControls.btn_reset.show();
			},
			continue_stopwatch_display: function() {
				interval_id = setInterval(interval_func, 100, interval_params);

				StopwatchControls.btn_flow.text('Pause');
				StopwatchControls.btn_reset.hide();
			},
			reset_stopwatch_display: function() {
				interval_params = {
					'h': 0,
					'm': 0,
					's': 0,
					'ms': 0
				};

				field_hour.nodeValue = '00';
				field_min.nodeValue = '00';
				field_sec.nodeValue = '00';

				StopwatchControls.btn_flow.text('Start');
				StopwatchControls.btn_reset.hide();
			}
		};
	}();
	stopwatch = $('<div></div>');
	Stopwatch.init(stopwatch);

	var TracStopwatchPlugin = {
		running: false,
		reset: false,
		use_value: false
	};
	StopwatchControls = function() {
		var btn_flow = $('<div style="float: left"></div>');
		var btn_reset = $('<div style="float: left">Reset</div>');

		btn_flow.click(function() {
			if (TracStopwatchPlugin.running) {
				toggler[0].firstChild.nodeValue = 'Use stopwatch value';
				toggler.show("fast");
				TracStopwatchPlugin.use_value = true;
				Stopwatch.pause_stopwatch_display();
			} else {
				toggler.hide("fast");
				TracStopwatchPlugin.use_value = false;
				Stopwatch.continue_stopwatch_display();
			}
			TracStopwatchPlugin.running = !TracStopwatchPlugin.running;
			TracStopwatchPlugin.reset = false;
		});

		btn_reset.click(function() {
			if (TracStopwatchPlugin.running) return;

			Stopwatch.reset_stopwatch_display();
			toggler[0].firstChild.nodeValue = 'Hide stopwatch';
			TracStopwatchPlugin.running = false;
			TracStopwatchPlugin.reset = true;
		});

		return {
			btn_flow: btn_flow,
			btn_reset: btn_reset,

			init: function(p_stopwatch) {
				p_stopwatch.append($('<div></div>')
					.append(btn_flow)
					.append(btn_reset));
			}
		};
	}();
	StopwatchControls.init(stopwatch);

	/* toggles the stopwatch (and controls) with a simple slide */
	toggler = $('<div>Show stopwatch</div>')
	toggler.toggle(
		function() {
			if (TracStopwatchPlugin.running)
				return false;
			if (TracStopwatchPlugin.use_value) {
				$("input#field-hours")[0].value = Math.round((
					Stopwatch.interval_params.h +
					Stopwatch.interval_params.m / 60 +
					Stopwatch.interval_params.s / 3600
				) * 100) / 100;
			}
			this.firstChild.nodeValue = 'Show stopwatch';
			stopwatch.hide("fast");
		},
		function() {
			if (TracStopwatchPlugin.reset)
				this.firstChild.nodeValue = 'Hide stopwatch';
			else
				this.firstChild.nodeValue = 'Use stopwatch value';
			stopwatch.show("fast");
		}
	);

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	$("input#field-hours").after(
		$('<div></div>')
		.append(toggler)
		.append(stopwatch));

	/* initialize */
	Stopwatch.reset_stopwatch_display();
	toggler.click();
})

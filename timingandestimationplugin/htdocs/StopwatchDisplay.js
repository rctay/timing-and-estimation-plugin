/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

/*
 * add buttons to control the stopwatch
 *
 * Button 'flow' has states: start -> stop <-> continue
 * Button 'reset' has state: reset
 */
jQuery(function($) {
	StopwatchDisplay = function() {
		/* the stopwatch (looks like 00:00:00) */
		var field_hour = $('<span>00</span>');
		var field_min = $('<span>00</span>');
		var field_sec = $('<span>00</span>');

		var display = $('<div></div>')
			.append(field_hour)
			.append(':')
			.append(field_min)
			.append(':')
			.append(field_sec);

		field_hour = field_hour[0].firstChild;
		field_min = field_min[0].firstChild;
		field_sec = field_sec[0].firstChild;

		var interval_id;
		var start_time = null;
		var total_time = 0;
		var now = function(){ return Math.floor((new Date()).getTime() / 1000);};
		var interval_func = function() {
			var interval = (now() - start_time) + total_time;
			var h = 0, m = 0, s = 0;
			s = interval % 60;
			m = Math.floor(interval/60) % 60;
			h = Math.floor(interval/3600);
			field_sec.nodeValue = s < 10 ? '0'+s : s;
			field_min.nodeValue = m < 10 ? '0'+m : m;
			field_hour.nodeValue = h < 10 ? '0'+h : h;
		};

		return {
			display: display,

			pause_stopwatch: function() {
				clearInterval(interval_id);
				interval_id = null;
				total_time += now() - start_time;
				start_time = null;
			},
			continue_stopwatch: function() {
				/*
				 * We really want to do an add (of the seconds on the display)
				 * - which is what we get when start_time is subtracted later.
				 */
				start_time = now();
				interval_id = setInterval(interval_func, 100);
			},
			reset_stopwatch: function() {
				field_hour.nodeValue = '00';
				field_min.nodeValue = '00';
				field_sec.nodeValue = '00';
				start_time = null;
				total_time = 0;
			},
			get_hours: function() {
				var total = total_time;
				if (start_time) total += now() - start_time;
				return Math.round((total / 3600) * 100) / 100;
			}
		};
	}();
});

/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

/*
 * add buttons to control the stopwatch
 *
 * Button 'flow' has states: start -> stop <-> continue
 * Button 'reset' has state: reset
 */
StopwatchDisplay = function() {
	/* the stopwatch (looks like 00:00:00) */
	var field_hour = $('<span>00</span>');
	var field_min = $('<span>00</span>');
	var field_sec = $('<span>00</span>');

	field_hour = field_hour[0].firstChild;
	field_min = field_min[0].firstChild;
	field_sec = field_sec[0].firstChild;

	var interval_id, interval_func;
	var p = {
		h: 0,
		m: 0,
		s: 0,
		ms: 0
	};
	var interval_func = function() {
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
		interval_params: p,

		init: function(p_stopwatch) {
			p_stopwatch
				.append(field_hour)
				.append(':')
				.append(field_min)
				.append(':')
				.append(field_sec);
		},
		pause_stopwatch: function() {
			clearInterval(interval_id);
			interval_id = null;
		},
		continue_stopwatch: function() {
			interval_id = setInterval(interval_func, 100);
		},
		reset_stopwatch: function() {
			p.h = 0;
			p.m = 0;
			p.s = 0;
			p.ms = 0;

			field_hour.nodeValue = '00';
			field_min.nodeValue = '00';
			field_sec.nodeValue = '00';
		}
	};
}();

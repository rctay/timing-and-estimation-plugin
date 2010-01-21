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

	var display = $('<div></div>')
		.append(field_hour)
		.append(':')
		.append(field_min)
		.append(':')
		.append(field_sec);

	field_hour = field_hour[0].firstChild;
	field_min = field_min[0].firstChild;
	field_sec = field_sec[0].firstChild;

	var interval_id, interval_func;
	var h = 0, m = 0, s = 0, ms = 0;
	var interval_func = function() {
		if (++ms>=10) {
			ms = 0;
			s++;
			field_sec.nodeValue = s < 10 ? '0'+s : s;
		}
		if (s>=60) {
			s = 0;
			m++;
			field_min.nodeValue = m < 10 ? '0'+m : m;
		}
		if (m>=60) {
			m = 0;
			h++;
			field_hour.nodeValue = h < 10 ? '0'+h : h;
		}
	};

	return {
		display: display,

		pause_stopwatch: function() {
			clearInterval(interval_id);
			interval_id = null;
		},
		continue_stopwatch: function() {
			interval_id = setInterval(interval_func, 100);
		},
		reset_stopwatch: function() {
			h = 0;
			m = 0;
			s = 0;
			ms = 0;

			field_hour.nodeValue = '00';
			field_min.nodeValue = '00';
			field_sec.nodeValue = '00';
		},
		get_hours: function() {
			return Math.round((
				h +
				m / 60 +
				s / 3600
			) * 100) / 100;
		}
	};
}();

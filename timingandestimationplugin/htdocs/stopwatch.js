/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var toggler, stopwatch;

	/* the stopwatch (looks like 00:00:00) */
	var field_hour = $('<span>00</span>');
	var field_min = $('<span>00</span>');
	var field_sec = $('<span>00</span>');

	stopwatch = $('<div></div>')
		.append(field_hour)
		.append(':')
		.append(field_min)
		.append(':')
		.append(field_sec);

	field_hour = field_hour[0].firstChild;
	field_min = field_min[0].firstChild;
	field_sec = field_sec[0].firstChild;

	/*
 	 * add buttons to control the stopwatch
	 *
	 * Button 'flow' has states: start -> stop <-> continue
	 * Button 'reset' has state: reset
	 */
	var btn_flow = $('<div style="float: left"></div>');
	var btn_reset = $('<div style="float: left">Reset</div>');
	stopwatch.append($('<div></div>')
		.append(btn_flow)
		.append(btn_reset));

	var interval_id, interval_func, interval_params;
	var pause_stopwatch_display = function() {
		clearInterval(interval_id);
		interval_id = null;

		btn_flow.text('Continue');
		btn_reset.show();
	};
	var continue_stopwatch_display = function() {
		interval_id = setInterval(function(p) {
			if (++p.ms>=10) {
				p.ms = 0;
				p.s++;
				field_sec.nodeValue = p.s < 10 ? '0'+p.s : p.s;
			}
			if (p.s>=600) {
				p.s = 0;
				p.m++;
				field_min.nodeValue = p.m < 10 ? '0'+p.m : p.m;
			}
			if (p.m>=60) {
				p.m = 0;
				p.h++;
				field_hour.nodeValue = p.h < 10 ? '0'+p.h : p.h;
			}
		}, 100, interval_params);

		btn_flow.text('Pause');
		btn_reset.hide();
	};
	var reset_stopwatch_display = function() {
		interval_params = {
			'h': 0,
			'm': 0,
			's': 0,
			'ms': 0
		};
		field_hour.nodeValue = '00';
		field_min.nodeValue = '00';
		field_sec.nodeValue = '00';

		btn_flow.text('Start');
		btn_reset.hide();
	};

	var running = 0;
	btn_flow.click(function() {
		if (running)
			pause_stopwatch_display();
		else
			continue_stopwatch_display();
		running = !running;
	});

	btn_reset.click(function() {
		if (running) return;

		reset_stopwatch_display();
		running = false;
	});

	/* toggles the stopwatch (and controls) with a simple slide */
	toggler = $('<div>Show stopwatch</div>')
	toggler.toggle(
		function() {
			this.firstChild.nodeValue = 'Show stopwatch';
			stopwatch.hide("fast");
		},
		function() {
			this.firstChild.nodeValue = 'Hide stopwatch';
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
	reset_stopwatch_display();
	toggler.click();
})

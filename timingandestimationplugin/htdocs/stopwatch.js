/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var toggler, stopwatch;

	/* the stopwatch (looks like 00:00:00) */
	var field_hour = $('<span></span>');
	var field_min = $('<span></span>');
	var field_sec = $('<span></span>');

	stopwatch = $('<div></div>')
		.append(field_hour)
		.append(':')
		.append(field_min)
		.append(':')
		.append(field_sec);

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

	var running = 0;
	var pause_stopwatch = function() {
		btn_flow.text('Continue');
		btn_reset.show();
	};
	var continue_stopwatch = function() {
		btn_flow.text('Pause');
		btn_reset.hide();
	};
	var reset_stopwatch = function() {
		btn_flow.text('Start');
		btn_reset.hide();
	};

	btn_flow.click(function() {
		if (running)
			pause_stopwatch();
		else
			continue_stopwatch();
		running = !running;
	});

	btn_reset.click(function() {
		if (running) return;

		reset_stopwatch();
		running = false;
	});

	/* toggles the stopwatch (and controls) with a simple slide */
	toggler = $('<div>Show stopwatch</div>')
	toggler.click(function() {
		stopwatch.toggle("fast");
	});

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	$("input#field-hours").after(
		$('<div></div>')
		.append(toggler)
		.append(stopwatch));
})

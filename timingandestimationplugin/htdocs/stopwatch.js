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

	/* toggles the stopwatch with a simple slide */
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

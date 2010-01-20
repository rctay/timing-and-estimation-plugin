/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var toggler, stopwatch;

	var field_hour = $('<span></span>');
	var field_min = $('<span></span>');
	var field_sec = $('<span></span>');

	stopwatch = $('<div></div>')
		.append(field_hour)
		.append(':')
		.append(field_min)
		.append(':')
		.append(field_sec);

	toggler = $('<div>Show stopwatch</div>')
	toggler.click(function() {
		stopwatch.toggle("fast");
	});

	$("input#field-hours").after(
		$('<div></div>')
		.append(toggler)
		.append(stopwatch));
})
